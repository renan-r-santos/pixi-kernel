###################################################################################################
# Environment builder
###################################################################################################
FROM ghcr.io/prefix-dev/pixi:319bb40faf2f12be48a3aae8b4f74d337763810630a5a78c5bb82d39f8566b9f as pixi-builder

ENV PIXI_LOCKED=true

WORKDIR /opt/binder

# Install environment
COPY .binder/pixi.toml pixi.toml
COPY .binder/pixi.lock pixi.lock
RUN pixi install && \
    pixi shell-hook --shell bash > /pixi-activate.sh && \
    chmod +x /pixi-activate.sh

# Clean up
RUN find .pixi \( -name '*.a' -o -name '*.pyc' -o -name '*.pyx' -o -name '*.pyo' \) -delete && \
    find .pixi -name '__pycache__' -type d -exec rm -rf '{}' '+'


###################################################################################################
# Final image
###################################################################################################
FROM ghcr.io/prefix-dev/pixi:319bb40faf2f12be48a3aae8b4f74d337763810630a5a78c5bb82d39f8566b9f

# https://mybinder.readthedocs.io/en/latest/tutorials/dockerfile.html
ARG NB_USER=jovyan
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}
ENV SHELL=/bin/bash

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

RUN echo '#!/bin/bash\n. /usr/local/share/pixi-activate.sh\nexec "$@"' > /usr/local/share/docker-entrypoint.sh && \
    chmod +x /usr/local/share/docker-entrypoint.sh

# Make sure the contents of this repo are in ${HOME} and owned by ${NB_USER}
COPY . ${HOME}
RUN mv ${HOME}/.binder/example ${HOME}/work && \
    chown -R ${NB_UID} ${HOME}

USER ${NB_USER}

# Copy the environment
COPY --from=pixi-builder /opt/binder/.pixi /opt/binder/.pixi
COPY --from=pixi-builder /pixi-activate.sh /usr/local/share/pixi-activate.sh

WORKDIR ${HOME}/work

# Install the example
RUN pixi install --manifest-path pixi.toml

ENTRYPOINT ["/usr/local/share/docker-entrypoint.sh"]
