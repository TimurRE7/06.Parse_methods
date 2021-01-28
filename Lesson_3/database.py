from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models


class Database:
    def __init__(self, db_url):
        engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=engine)
        self.maker = sessionmaker(bind=engine)

    def get_or_create(self, session, model, data):
        db_model = session.query(model).filter(model.url == data['url']).first()
        if not db_model:
            db_model = model(**data)
        return db_model

    def get_or_create_comment(self, session, model, data):
        comment_data = data.copy()
        del comment_data['author']
        db_model = session.query(model).filter(model.comment_id == comment_data['comment_id']).first()
        if not db_model:
            db_model = model(**comment_data)
        return db_model

    def get_or_create_comment_author(self, session, model, data):
        author_data = data['author']
        db_model = session.query(model).filter(model.url == author_data['url']).first()
        if not db_model:
            db_model = model(**author_data)
        return db_model

    def create_post(self, data: dict):
        session = self.maker()
        tags = map(lambda tag_data: self.get_or_create(session, models.Tag, tag_data), data['tags'])
        author = self.get_or_create(session, models.Author, data['author'])
        post = self.get_or_create(session, models.Post, data['post_data'])
        image = self.get_or_create(session, models.Images, data['image'])
        comment = map(lambda comment_data: self.get_or_create_comment(session, models.Comments, comment_data),
                      data['comments'])
        comment_author = map(
            lambda comment_data: self.get_or_create_comment_author(session, models.Author, comment_data), data['comments'])
        post.author = author
        post.tags.extend(tags)
        post.image = image
        post.comments.extend(comment)
        # post.author.extend(comment_author)
        if post.comments:
            post.comment_author.extend(comment_author)

        # comments.

        session.add(post)

        try:
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()

    # def create_post_comment(self, comments_data):
    #     session = self.maker()
    #     comment =
