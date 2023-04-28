FROM python:3.9.12

LABEL maintainer="Bittrap Team <info@bittrap.com>"

ENV ELECTRUM_CHECKSUM_SHA512=5b968814c2df5530fe3149915134c6faf054472bc9cd4fc36978ac3597869333c181ff7805a643647b7a9158d8aa7de0e5c375189103643eba1b3ac03b416893
ENV ELECTRUM_VERSION=4.3.1
ENV PIP_ROOT_USER_ACTION=ignore

RUN apt-get update && \
    apt-get install -y python3-pyqt5 libsecp256k1-0 python3-cryptography && \
    wget https://download.electrum.org/${ELECTRUM_VERSION}/Electrum-${ELECTRUM_VERSION}.tar.gz && \
    [ "${ELECTRUM_CHECKSUM_SHA512}  Electrum-${ELECTRUM_VERSION}.tar.gz" = "$(sha512sum Electrum-${ELECTRUM_VERSION}.tar.gz)" ] && \
    echo -e "Checksum OK"

RUN python -m pip install --upgrade pip && \
    pip3 install --user base58==2.1.1 && \
    pip3 install --user cryptography==37.0.4 && \
    pip3 install --user eciespy==0.3.13 && \
    pip3 install --user pyqt5==5.15.7 && \
    pip3 install --user gql[requests]==3.4.0 && \
    pip3 install --user Electrum-${ELECTRUM_VERSION}.tar.gz && \
    rm -f Electrum-${ELECTRUM_VERSION}.tar.gz

WORKDIR /root
USER root
COPY . /root

ENTRYPOINT ["python", "main.py"]
