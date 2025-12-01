A httpx client with conda authentication and telemetry support.

Adapts conda's requests-based auth handler plugins to httpx, automatically
loading conda-provided credentials as necessary.

## Project Goals

* Provide a single `httpx.Client` and `httpx.AsyncClient` that authenticates to conda services, in the same way that conda's `get_session(url)` does but without requiring a separate client per URL.
* Support existing conda authentication plugins.
* Support other conda plugins that modify headers sent during requests, such as telemetry plugins.
* Improve efficiency of conda authentication by avoiding `Channel()` calls when possible.
* Avoid token-in-URL forms of authentication.
* Support `truststore`.
* Support proxy configuration from conda.
* Interoperate with Python software that wants a httpx client.
* Have excellent test coverage.

## Conda features which can affect request headers

* [Request Headers](https://docs.conda.io/projects/conda/en/stable/dev-guide/plugins/request_headers.html) plugins, `conda_session_headers`, `conda_request_headers` as [get_cached_*_headers()](https://github.com/conda/conda/blob/main/conda/plugins/manager.py#L103-L104) on CondaPluginManager
* [Auth Handlers](https://docs.conda.io/projects/conda/en/stable/dev-guide/plugins/auth_handlers.html) plugins, configurable per channel.
* [CondaHttpAuth](https://github.com/conda/conda/blob/main/conda/gateways/connection/session.py#L258), predates the plugin API, supports binstar tokens and Proxy-Authorization.

## Projects which can affect requests headers

* [conda-anaconda-telemetry](https://github.com/anaconda/conda-anaconda-telemetry/blob/main/conda_anaconda_telemetry/hooks.py) using `conda_request_headers` plugin hook.
* [anaconda-auth](https://github.com/anaconda/anaconda-auth), a CLI to set up authentication to Anaconda services. [AnacondaAuthHandler](https://github.com/anaconda/anaconda-auth/blob/main/src/anaconda_auth/_conda/auth_handler.py#L49) loads the token.
* [conda-auth](https://github.com/conda-incubator/conda-auth)
