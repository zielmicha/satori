#!/bin/bash
OFFICE=$(dirname "$(readlink -f "$(which "$0")")")
pushd "${OFFICE}"
source ./settings.sh

TAG=judge

rm -rf "${TAG}"
mkdir -p "${TAG}"
add_header "${TAG}" "${DOCKER_REPO}:base"
add_apt_cacher "${TAG}"

cat >> "${TAG}/Dockerfile" <<EOF
RUN apt-add-repository "ppa:satoriproject/satori"
RUN apt-get update
RUN apt-get -y dist-upgrade
RUN apt-get --no-install-recommends -f -y install ${JUDGE_PACKAGES}
RUN apt-get install libssh2-1
ADD tcs-scripts /root/tcs-scripts
RUN /root/tcs-scripts/tcs-scripts
RUN rm -rf /root/tcs-scripts
RUN apt-get -y autoremove
RUN apt-get -y clean
EOF

rem_apt_cacher "${TAG}"
add_footer "${TAG}"

copy_scripts "${TAG}"

if [ "$1" != "debug" ]; then
    docker build "--tag=${DOCKER_REPO}:${TAG}" "${TAG}"
fi

popd
