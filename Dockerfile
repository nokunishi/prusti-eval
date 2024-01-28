# this method causes issues when building qrates with cargo
# i.e.) error: crate `md5` required to be available in rlib format, but was not found in this form
# 196 similar issues get reported

# docker run --privileged -d --name p1 docker:dind
# docker exec -it p1 /bin/sh
# docker pull ubuntu

# OR 
#docker run -v /var/run/docker.sock:/var/run/docker.sock -ti ubuntu
#docker exec -it <CONTAINER_ID> /bin/sh
#once inside the container
#docker container run -d --name=sock-nginx nginx\

#docker start -a  vigorous_napier
#docker exec -it -u root 28781d201aa1 bin/sh


# if it's too slow 
# RUN git config --global core.compression 0
# RUN git clone --depth 1 https://github.com/rust-corpus/qrates.git
# RUN cd qrates
# RUN git fetch --unshallow && pull --all

FROM ubuntu:latest

#setup ubuntu
RUN apt-get update && apt-get install git && apt-get install sudo
RUN echo "clone qrates from git repo"
RUN git clone https://github.com/rust-corpus/qrates.git
RUN cd qrates
RUN echo "git cloned succesfully"
CMD [ "setup" ]

#install rust
#apk add build-base
RUN apt-get install curl && apt install build-essential && apt install pkg-config && apt install libssl-dev
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh 
RUN  . "$HOME/.cargo/env" 
# RUN source "$HOME/.cargo/env" 
RUN cargo build --all --release

# make sure to create a CrateList.json

FROM rust:latest
RUN echo "build project"
RUN cargo build --all --release

