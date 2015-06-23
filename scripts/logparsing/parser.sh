# call this like
# bash scripts/logparsing/parser.sh example.log
# or maybe
# bash scripts/logparsing/parser.sh example.log | head
# to get a list most accessed views

cut -d ' ' -f7 $1 | ./manage.py resolve_urls | python scripts/logparsing/analyzelogs.py
