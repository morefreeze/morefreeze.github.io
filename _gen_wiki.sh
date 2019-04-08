ROOT=$(dirname "$0")
cd "$ROOT/_wiki" && pipenv run simiki generate
