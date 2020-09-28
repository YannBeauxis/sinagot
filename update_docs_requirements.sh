DOCS_PATH=docs
REQUIREMENTS_PATH=$DOCS_PATH/requirements.txt
SINAGOT_VERSION=$(poetry run python -c 'import sinagot; print(sinagot.__version__)')
SINAGOT_BUILD=sinagot-$SINAGOT_VERSION.tar.gz

poetry build
rm $DOCS_PATH/sinagot-*.whl
cp dist/$SINAGOT_BUILD docs/$SINAGOT_BUILD
poetry export -f requirements.txt --dev --without-hashes -o $REQUIREMENTS_PATH
echo "./docs/$SINAGOT_BUILD" >> $REQUIREMENTS_PATH