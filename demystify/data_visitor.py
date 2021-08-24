from antlr4 import *
from grammar.DemystifyVisitor import DemystifyVisitor

class DemystifyDataVisitor(DemystifyVisitor):
    def visitCard_mana_cost(self, ctx):
        # TODO stub
        mana = self.visitMana(ctx.mana())

    def visitMana(self, ctx):
        # TODO stub
        ctx.MANA_SYM
        return ctx

# TODO TypeLineVisitor
# TODO RulesTextVisitor
