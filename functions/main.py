import sys
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from firebase_functions.options import CorsOptions, set_global_options
from firebase_admin import initialize_app
from firebase_functions.https_fn import on_request, Response, Request
from nips_chat_api.chat_api import prediction

set_global_options(max_instances=1)

initialize_app()


@on_request(cors=CorsOptions(
    cors_origins=[r"nbuild\.io$"],
    cors_methods=["post"],
))
def predict(req: Request) -> Response:
  data = req.get_json(silent=True)
  user_q = data.get("user_q", "") if data else ""
  return Response(prediction(user_q), content_type="plain/text")
