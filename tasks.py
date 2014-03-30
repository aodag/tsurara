from invoke import run, task
from whitenoise import WhiteNoise
from tsurara.startup import startup
from biscuit.blog import Application
import waitress
from webassets.loaders import YAMLLoader
from webassets import Environment, Bundle
from repoze.tm import TM
from backlash import DebuggedApplication

#assets = YAMLLoader('biscuit.blog.assets.yaml').load_environment()
#print(list(assets['js-all'].urls()))
assets = Environment('apps/biscuit.blog.assets', 'http://cdn.example.com/')
js = Bundle(
    'bower_components/jquery/dist/jquery.js',
    'bower_components/bootstrap/dist/js/bootstrap.js',
    #filters='jsmin',
    #output='gen/all.js',
)
css = Bundle(
    'bower_components/bootstrap/dist/css/bootstrap.css',
    output='gen/all.css')

assets.register('js-all', js)
assets.register('css-all', css)


@task
def build_assets():
    for b in assets:
        b.build()

@startup(Application, {"assets": assets})
def make_blog_app(builder):
    from sqlalchemy import create_engine
    from biscuit.blog.models import Base, DBSession, Blog
    import os
    here = os.getcwd()
    engine = create_engine("sqlite:///%(here)s/blog.sqlite" % {'here': here},
                           echo=True)
    Base.metadata.create_all(bind=engine)  # should use alembic
    DBSession.configure(bind=engine)
    if not Blog.query.filter(Blog.default).count():
        blog = Blog(name='default', title=u'ブログだよ')
        DBSession.add(blog)
        import transaction
        transaction.commit()

    builder.use(WhiteNoise, root=assets.directory)
    builder.use(TM)
    builder.use(DebuggedApplication)

@task
def run_blog():
    app = make_blog_app()
    waitress.serve(app)
