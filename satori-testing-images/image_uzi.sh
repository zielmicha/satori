#!/bin/bash
OFFICE=$(dirname "$(readlink -f "$(which "$0")")")
pushd "${OFFICE}"
source ./settings.sh

TAG=uzi
BUILDDIR="build-${TAG}"

rm -rf "${BUILDDIR}"
mkdir -p "${BUILDDIR}"
add_header "${BUILDDIR}" "${DOCKER_REPO}:judge"
add_apt_cacher "${BUILDDIR}"

cat >> "${BUILDDIR}/Dockerfile" <<EOF
RUN apt-add-repository "deb http://dl.google.com/linux/deb/ stable main"
RUN apt-add-repository "deb http://dl.google.com/linux/chrome/deb/ stable main"
RUN apt-add-repository "deb http://dl.google.com/linux/talkplugin/deb/ stable main"
RUN apt-key adv --keyserver "${KEYSERVER}" --recv-key A040830F7FAC5991
RUN apt-get update
RUN apt-get -y dist-upgrade
RUN apt-get --no-install-recommends -f -y install ${UZI_PACKAGES}
RUN apt-get -f -y install nvidia-304 linux-headers-generic

RUN rm -rf /root/tcs-scripts
ADD tcs-scripts /root/tcs-scripts
RUN /root/tcs-scripts/tcs-scripts
RUN rm -rf /root/tcs-scripts
RUN apt-get -y autoremove
RUN apt-get -y clean
EOF

rem_apt_cacher "${BUILDDIR}"
add_footer "${BUILDDIR}"

copy_scripts "${TAG}" "${BUILDDIR}"

if [ "$1" != "debug" ]; then
    unshare -m docker -- build "$@" "--tag=${DOCKER_REPO}:${TAG}" "${BUILDDIR}"
fi

popd
