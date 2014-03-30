from whitenoise import WhiteNoise
from tsurara.startup import startup
from biscuit.blog.wsgiapp import application

@startup(application, {})
def setup(builder):
    builder.use(WhiteNoise, root="apps/biscuit.blog.assets")
