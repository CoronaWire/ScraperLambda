rm -rf ../crawlerZipTmp
rm -rf ../AWSCrawlerLambda.zip
mkdir ../crawlerZipTmp

cp -a ./. ../crawlerZipTmp/

rm -rf ../crawlerZipTmp/v-env

# Copy all user python packages to a tmp directory
# To find out where user python packages are installed on your machine
# $ python -m site   OR   $ python -m site --user-site
cp -a ./v-env/lib/python2.7/site-packages/. ../crawlerZipTmp/
cp -a ./v-env/lib64/python2.7/site-packages/. ../crawlerZipTmp/
# cp -a ../LambdaEnvironment/.local ../crawlerZipTmp/.local

# Remove all unused python files
# rm -rf ../crawlerZipTmp/wheel*

cd ../crawlerZipTmp && zip -r9 ../AWSCrawlerLambda.zip .
cd ../ScraperLambda
