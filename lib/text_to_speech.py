import google.oauth2.service_account
import google.cloud.speech_v1


class GoogleSpeechToText:
	def __init__(self, endpoint, lang, recognition_model, api_credentials = None):
		credentials = google.oauth2.service_account.Credentials.from_service_account_file(api_credentials) if api_credentials else grpc.local_channel_credentials()
		LocalSpeechGrpcTransport = type('LocalSpeechGrpcTransport', (google.cloud.speech_v1.gapic.transports.speech_grpc_transport.SpeechGrpcTransport, ), dict(create_channel = lambda self, address, credentials, **kwargs: grpc.secure_channel(address, credentials, **kwargs)))
		client_options = dict(api_endpoint = endpoint)

		self.client = google.cloud.speech_v1.SpeechClient(credentials = credentials, client_options = client_options) if api_credentials else google.cloud.speech_v1.SpeechClient(transport = LocalSpeechGrpcTransport(address = endpoint, credentials = credentials), client_options = client_options)
		self.lang = lang
		self.recognition_model = recognition_model

	def transcribe(self, pcm_s16le, sample_rate, num_channels):
		res = self.client.recognize(dict(audio_channel_count = num_channels, encoding = 'LINEAR16', sample_rate_hertz = sample_rate, language_code = self.lang, model = self.recognition_model), dict(content = pcm_s16le))
		hyp = res.results[0].alternatives[0].transcript if len(res.results) > 0 else ''
		return hyp
