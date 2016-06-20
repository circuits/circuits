#!/bin/bash

if [[ $TRAVIS_OS_NAME == "osx" ]]; then
  case "${TOXENV}" in
    py27)
      brew install python
    ;;
    py35)
      brew install python3
    ;;
    pypy)
      brew install pypy
    ;;
  esac
fi
