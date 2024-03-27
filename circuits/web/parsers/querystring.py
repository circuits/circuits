from urllib.parse import parse_qsl


class QueryStringToken:
    ARRAY = 'ARRAY'
    OBJECT = 'OBJECT'
    KEY = 'KEY'


class QueryStringParser:
    def __init__(self, data) -> None:
        self.result = {}

        sorted_pairs = self._sorted_from_string(data) if isinstance(data, str) else self._sorted_from_obj(data)

        [self.process(x) for x in sorted_pairs]

    def _sorted_from_string(self, data):
        stage1 = parse_qsl(data, keep_blank_values=True)
        stage2 = [(x[0].strip(), x[1].strip()) for x in stage1]
        return sorted(stage2, key=lambda p: p[0])

    def _sorted_from_obj(self, data):
        # data is a list of the type generated by parse_qsl
        if isinstance(data, list):
            items = data
        else:
            # complex objects:
            try:
                # django.http.QueryDict,
                items = [(i[0], j) for i in data.lists() for j in i[1]]
            except AttributeError:
                # webob.multidict.MultiDict
                # werkzeug.datastructures.MultiDict
                items = data.items()

        return sorted(items, key=lambda p: p[0])

    def process(self, pair) -> None:
        key = pair[0]
        value = pair[1]

        # faster than invoking a regex
        try:
            key.index('[')
            self.parse(key, value)
            return
        except ValueError:
            pass

        try:
            key.index('.')
            self.parse(key, value)
            return
        except ValueError:
            pass

        self.result[key] = value

    def parse(self, key, value) -> None:
        ref = self.result
        tokens = self.tokens(key)

        for token in tokens:
            token_type, key = token

            if token_type == QueryStringToken.ARRAY:
                if key not in ref:
                    ref[key] = []
                ref = ref[key]

            elif token_type == QueryStringToken.OBJECT:
                if key not in ref:
                    ref[key] = {}
                ref = ref[key]

            elif token_type == QueryStringToken.KEY:
                try:
                    ref = ref[key]
                    next(tokens)
                # TypeError is for pet[]=lucy&pet[]=ollie
                # if the array key is empty a type error will be raised
                except (IndexError, KeyError, TypeError):
                    # the index didn't exist
                    # so we look ahead to see what we are setting
                    # there is not a next token
                    # set the value
                    try:
                        next_token = next(tokens)

                        if next_token[0] == QueryStringToken.ARRAY:
                            ref.append([])
                            ref = ref[key]
                        elif next_token[0] == QueryStringToken.OBJECT:
                            try:
                                ref[key] = {}
                            except IndexError:
                                ref.append({})

                            ref = ref[key]
                    except StopIteration:
                        try:
                            ref.append(value)
                        except AttributeError:
                            ref[key] = value
                        return

    def tokens(self, key):
        buf = ''
        for char in key:
            if char == '[':
                yield QueryStringToken.ARRAY, buf
                buf = ''

            elif char == '.':
                yield QueryStringToken.OBJECT, buf
                buf = ''

            elif char == ']':
                try:
                    yield QueryStringToken.KEY, int(buf)
                    buf = ''
                except ValueError:
                    yield QueryStringToken.KEY, None
            else:
                buf = buf + char

        if len(buf) > 0:
            yield QueryStringToken.KEY, buf
