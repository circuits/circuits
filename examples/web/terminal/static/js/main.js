var options = {
    custom_prompt: "&gt;&gt;&gt; ",
    hello_message: "Welcome! Type \'help\' for, well, help."
}

function main() {
    $("#terminal").height($(document).height());
    $("#terminal").terminal("/", options);
}
