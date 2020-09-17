REQUIREMENTS_PATH=docs/requirements.txt

poetry export -f requirements.txt --dev --without-hashes -o $REQUIREMENTS_PATH
echo "sinagot==$(poetry run python -c 'import sinagot; print(sinagot.__version__)')" >> $REQUIREMENTS_PATH