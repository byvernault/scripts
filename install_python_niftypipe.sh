# install python first
install_path='/Users/byvernault/home-local/code/Python_2.7.11'

if [ ! -f ${install_path}/bin/python ]
then
    cd ${install_path}
    python_version=2.7.11
    url="https://www.python.org/ftp/python/${python_version}/Python-${python_version}.tgz"
    if [ "`uname`" == "Darwin" ]
    then
	curl $url -o Python-${python_version}.tgz
    else
	wget $url
    fi
    tar -xzvf Python-${python_version}.tgz
    cd ${install_path}/Python-${python_version}
    ./configure --prefix=${install_path}
    make -j4 && make install
fi

if [ ! -f ${install_path}/bin/python ]
then
    echo "Error while installing python. exit."
    exit
fi

# Download and install easy_install and pip
if [ ! -f ${install_path}/bin/pip ]
then
    cd ${install_path}
    url="https://bootstrap.pypa.io/get-pip.py"
    if [ "`uname`" == "Darwin" ]
    then
	curl $url -o get-pip.py
    else
	wget $url
    fi
    ${install_path}/bin/python get-pip.py
fi


# Download and install dependencies
${install_path}/bin/pip install numpy
${install_path}/bin/pip install scipy
${install_path}/bin/pip install nibabel
${install_path}/bin/pip install pydicom
