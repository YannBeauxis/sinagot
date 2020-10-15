[[ $(pwd) =~ ([a-z\-]*)$ ]]
PACKAGE_NAME=${BASH_REMATCH[1]/-/_}
DOCS_PATH=docs
REQUIREMENTS_PATH=$DOCS_PATH/requirements.txt
PACKAGE_VERSION=$(poetry run python -c "import $PACKAGE_NAME; print($PACKAGE_NAME.__version__)")
echo "version $PACKAGE_VERSION"
PACKAGE_BUILD=$PACKAGE_NAME-$PACKAGE_VERSION.tar.gz

poetry build -q
rm $DOCS_PATH/$PACKAGE_NAME-*.tar.gz
cp dist/$PACKAGE_BUILD docs/$PACKAGE_BUILD
poetry export -f requirements.txt --dev --without-hashes -E dask -o $REQUIREMENTS_PATH
echo "./docs/$PACKAGE_BUILD" >> $REQUIREMENTS_PATH