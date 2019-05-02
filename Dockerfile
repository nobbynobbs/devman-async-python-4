FROM python:3.7-alpine as whl-build
RUN pip install poetry==0.12.12
WORKDIR /tmp
COPY poetry.lock /tmp/poetry.lock
COPY pyproject.toml /tmp/pyproject.toml
COPY minechat_client /tmp/minechat_client
RUN poetry build


FROM python:3.7-alpine
COPY --from=whl-build /tmp/dist/minechat_client-*-py3-none-any.whl /tmp
RUN pip install /tmp/minechat_client-*-py3-none-any.whl \
  && mkdir -p /var/minechat/ && chmod -R 777 /var/minechat/
ENV MINECHAT_HISTORY=/var/minechat/minechat.history
ENTRYPOINT [ "minechat" ]
