from todo.models import BaseModelFieldsMixin


class Project(BaseModelFieldsMixin):
    def __str__(self):
        return self.title
