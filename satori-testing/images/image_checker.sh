#!/bin/bash
OFFICE=$(dirname "$(readlink -f "$(which "$0")")")
pushd "${OFFICE}"
source ./settings.sh

TAG=checker

rm -rf ".${TAG}"
mkdir -p ".${TAG}"
cat > ".${TAG}/Dockerfile" <<EOF
FROM tcs:judge
MAINTAINER ${MAINTAINER}

ENV DEBIAN_PRIORITY critical
ENV DEBIAN_FRONTEND noninteractive
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

RUN echo "Acquire::http::Proxy \"${APTCACHER}\";" > /etc/apt/apt.conf.d/90apt-cacher

RUN apt-get-keys
RUN apt-get --no-install-recommends -f -y install ${CHECKER_PACKAGES}
RUN apt-get -f -y install nvidia-cuda-toolkit nvidia-331 linux-headers-generic

RUN hg clone https://bitbucket.org/satoriproject/satori /root/satori
RUN /root/satori/install_judge.sh
RUN rm -rf /root/satori

RUN apt-get autoremove
RUN apt-get clean

ADD tcs-scripts /root/tcs-scripts
RUN /root/tcs-scripts/tcs-scripts
RUN rm -rf /root/tcs-scripts

RUN rm -f /etc/apt/apt.conf.d/90apt-cacher
EOF

cp -a tcs-scripts ".${TAG}"
if [ -d "tcs-debs-${TAG}" ]; then
    cp -a "tcs-debs-${TAG}" ".${TAG}"/tcs-scripts/debs
fi

if [ "$1" != "debug" ]; then
    docker build "--tag=tcs:${TAG}" ".${TAG}"
fi

popd
