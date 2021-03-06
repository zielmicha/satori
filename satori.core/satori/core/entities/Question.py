# vim:ts=4:sts=4:sw=4:expandtab

from django.db import models

from satori.core.dbev   import Events
from satori.core.models import Entity

@ExportModel
class Question(Entity):
    """Model. Description of a question.
    """
    parent_entity = models.OneToOneField(Entity, parent_link=True, related_name='cast_question')

    problem       = models.ForeignKey('ProblemMapping', null=True, related_name='questions', on_delete=models.CASCADE)
    contest       = models.ForeignKey('Contest', related_name='questions', on_delete=models.CASCADE)
    inquirer      = models.ForeignKey('Role', related_name='questions', on_delete=models.PROTECT)
    content       = models.TextField(blank=True)
    date_created  = models.DateTimeField(auto_now_add=True)
    
    answer        = models.TextField(blank=True, null=True)
    answer_files  = AttributeGroupField(PCArg('self', 'VIEW'), PCArg('self', 'MANAGE'), '')

    class ExportMeta(object):
        fields = [('problem', 'VIEW'), ('contest', 'VIEW'), ('inquirer', 'VIEW'), ('content', 'VIEW'), ('answer', 'VIEW'), ('date_created', 'VIEW')]

    class RightsMeta(object):
        inherit_parent = 'contest'
        inherit_parent_require = 'VIEW'

        inherit_parent_MANAGE = ['MANAGE']

    def save(self, *args, **kwargs):
        self.fixup_answer_files()
        return super(Question, self).save(*args, **kwargs)

    @classmethod
    def inherit_rights(cls):
        inherits = super(Question, cls).inherit_rights()
        cls._inherit_add(inherits, 'MANAGE', 'contest', 'MANAGE')
        return inherits

    @ExportMethod(DjangoStruct('Question'), [DjangoStruct('Question')], PCArgField('fields', 'contest', 'ASK_QUESTIONS'), [CannotSetField])
    @staticmethod
    def create(fields):
        question = Question()
        if fields.problem is not None and fields.problem.contest != fields.contest:
            raise CannotSetField(field='problem')
        question.forbid_fields(fields, ['answer', 'date_created', 'inquirer'])
        question.update_fields(fields, ['problem', 'contest', 'content'])
        role = question.contest.find_contestant(token_container.token.role)
        if role is None:
            role = token_container.token.role
        question.inquirer = role
        question.save()
        Privilege.grant(role, question, 'VIEW')
        return question

    @ExportMethod(DjangoStruct('Question'), [DjangoId('Question'), DjangoStruct('Question')], PCArg('self', 'MANAGE'), [CannotSetField, SphinxException])
    def modify(self, fields):
        self.forbid_fields(fields, ['id', 'contest', 'problem'])
        self.update_fields(fields, ['answer', 'date_created', 'content'])
        self.save()
        if self.answer is not None:
            self.answer_files_set_map(render_sphinx(self.answer, self.answer_files_get_map()))
        return self
 
    @ExportMethod(NoneType, [DjangoId('Question')], PCArg('self', 'MANAGE'), [CannotDeleteObject])
    def delete(self):
        try:
            super(Question, self).delete()
        except models.ProtectedError as e:
            raise CannotDeleteObject()


class QuestionEvents(Events):
    model = Question
    on_insert = on_update = ['topic', 'time']
    on_delete = []
