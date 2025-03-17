from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

from somisana.config import somisana_config


engine = create_engine(
    somisana_config.SOMISANA.DB.URL,
    echo=somisana_config.SOMISANA.DB.ECHO,
    isolation_level=somisana_config.SOMISANA.DB.ISOLATION_LEVEL,
    future=True,
)

Session = scoped_session(
    sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        future=True,
    )
)


class _Base:
    def save(self):
        Session.add(self)
        Session.flush()

    def delete(self):
        Session.delete(self)
        Session.flush()

    def __repr__(self):
        try:
            params = ', '.join(f'{attr}={getattr(self, attr)!r}' for attr in getattr(self, '_repr_'))
            return f'{self.__class__.__name__}({params})'
        except AttributeError:
            return object.__repr__(self)


Base = declarative_base(cls=_Base)
