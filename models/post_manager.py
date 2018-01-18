from models.models import PostModel ,UserModel ,CommentsModel

from models.base_manager import SNBaseManager
from models.user_manager import UserManager



class PostManager(SNBaseManager):

    def __init__(self):
        class_model = PostModel
        super(PostManager, self).__init__(class_model)

    def get_posts(self,user):
        return self.select().And([('user','=',user.object.id)]).run()

    def save_post(self,form, user):
        self.object.title = form.get('title', '')
        self.object.photos = form.get('photos', '')
        self.object.text = form.get('text', '')
        self.object.user = user.object
        self.save()

    def _get_post_id(self, id):
        return self.select().And([('id', '=', str(id))]).run()

    def add_comment(self,comment,user,post):
        if not isinstance(post, PostModel):
            post = self.get_post(post)
        if not isinstance(user, UserModel):
            user = UserManager().get_user(user)

        comment_manager = SNBaseManager(CommentsModel)
        comment_manager.object.text = comment
        comment_manager.object.post = post
        comment_manager.object.user = user
        comment_manager.save()


