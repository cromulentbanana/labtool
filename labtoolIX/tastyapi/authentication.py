from tastypie.authentication import BasicAuthentication, SessionAuthentication, ApiKeyAuthentication, MultiAuthentication

DefaultAuthentication = lambda: MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), BasicAuthentication())

