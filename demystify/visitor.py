from typing import Iterable, Tuple

from inflection import singularize

from grammar.DemystifyVisitor import DemystifyVisitor

from mtg_types import Ability, AtomicEffect, Duration, KeywordAbility, KeywordLine, Line, Mana, ManaSymbol, Sentence, Typeline

def flatten(container: Iterable):
    for i in container:
        if isinstance(i, (list, tuple)):
            yield from flatten(i)
        else:
            yield i

class DemystifyDataVisitor(DemystifyVisitor):

    # Utility methods
    # Visit everything in a context list
    def map_visit(self, ctx):
        if ctx is None:
            return []
        else:
            return list(map(lambda c: self.visit(c), ctx))

    # Terminal
    def visitTerminal(self, node) -> str:
        return singularize(node.getText())


    # Start rule cardManaCost
    def visitCardManaCost(self, ctx) -> Mana:
        return self.visit(ctx.mana())

    def visitMana(self, ctx) -> Mana:
        return self.map_visit(ctx.manaSymbol())

    def visitManaSymbol(self, ctx) -> ManaSymbol:
        return ManaSymbol.from_str(self.visitChildren(ctx))


    # Start rule typeline
    def visitTypeline(self, ctx) -> Typeline:
        supertypes = self.map_visit(ctx.supertype())
        cardTypes = self.map_visit(ctx.cardType())
        subtypes = self.map_visit(ctx.subtype())
        return Typeline(cardTypes, supertypes=supertypes, subtypes=subtypes)


    # Start rule rulesText
    def visitRulesText(self, ctx) -> list[Line]:
        return self.map_visit(ctx.line())

    def visitKeywordLine(self, ctx) -> KeywordLine:
        return self.map_visit(ctx.keywordAbility())

    def visitKeywordAbilityIntCost(self, ctx) -> KeywordAbility:
        return KeywordAbility(
            self.visit(ctx.kw),
            arg_int=None if ctx.keywordArgInt() is None else self.visit(ctx.keywordArgInt()),
            arg_cost=None if ctx.keywordArgCost() is None else self.visit(ctx.keywordArgCost()))

    def visitKeywordAbilityFrom(self, ctx) -> KeywordAbility:
        return KeywordAbility(
            self.visit(ctx.keywordFrom()),
            arg_from=self.map_visit(ctx.keywordArgFrom()))

    def visitKeywordAbilityQuality(self, ctx) -> KeywordAbility:
        return KeywordAbility(
            ctx.kw.text,
            arg_quality=self.visit(ctx.keywordArgQuality()))

    def visitKeywordAbilityQualityCost(self, ctx) -> KeywordAbility:
        return KeywordAbility(
            ctx.kw.text,
            arg_quality=self.visit(ctx.keywordArgQuality()),
            arg_cost=self.visit(ctx.keywordArgCost()))

    def visitAbility(self, ctx) -> Ability:
        effect = self.visit(ctx.spellEffect())
        if ctx.cost() is not None:
            cost = self.visit(ctx.cost())
            return Ability("activated", effect, cost=cost)
        elif ctx.trigger() is not None:
            trigger = self.visit(ctx.trigger())
            return Ability("triggered", effect, trigger=trigger)
        else:
            return Ability("static", effect)

    def visitSpellEffect(self, ctx) -> list[Sentence]:
        return self.map_visit(ctx.atomicEffect())

    def visitAtomicEffect(self, ctx) -> AtomicEffect:
        game_action = self.visit(ctx.gameAction())
        duration = self.visit(ctx.duration())
        condition = self.visit(ctx.fullCondition())
        return AtomicEffect(game_action, duration=duration, condition=condition)

    def visitGameAction(self, ctx) -> Sentence:
        if ctx.subsetList() is not None:
            subj = self.visit(ctx.subsetList())
        else:
            subj = "you"
        action, dir_obj, ind_obj = self.visit(ctx.keywordAction())
        return Sentence(subj, action, direct_obj=dir_obj, indirect_obj=ind_obj)

    def visitKeywordActionIntransitive(self, ctx) -> Tuple[str, None, None]:
        return (ctx.verb.text, None, None)

    def visitKeywordActionSubset(self, ctx) -> Tuple[str, str, None]:
        return (ctx.verb.text, self.visit(ctx.subsetList()), None)

    def visitKeywordActionNumber(self, ctx) -> Tuple[str, None, str]:
        return (ctx.verb.text, None, self.visit(ctx.number()))

    def visitKeywordActionDamage(self, ctx) -> Tuple[str, str, str]:
        return (ctx.verb.text, self.visit(ctx.subsetList()), self.visit(ctx.number()))

    def visitKeywordActionTwoSubsets(self, ctx) -> Tuple[str, str, str]:
        subsetList = ctx.subsetList()
        if ctx.conj.text == 'from':
            return (ctx.verb.text, self.visit(subsetList[0]), self.visit(subsetList[1]))
        else:
            return (ctx.verb.text, self.visit(subsetList[1]), self.visit(subsetList[0]))

    def visitKeywordActionMana(self, ctx) -> Tuple[str, None, str]:
        return (ctx.verb.text, None, self.visit(ctx.mana()))

    def visitKeywordActionPT(self, ctx) -> Tuple[str, None, str]:
        return (ctx.verb.text, None, self.visit(ctx.pt()))

    def visitKeywordActionName(self, ctx) -> Tuple[str, None, str]:
        return (ctx.verb.text, None, ctx.name.text)

    def visitKeywordActionPutCounter(self, ctx) -> Tuple[str, str, str]:
        return (ctx.verb.text, self.visit(ctx.subsetList()), self.visit(ctx.counterSubset()))

    def visitKeywordActionBecome(self, ctx) -> Tuple[str, str, str|None]:
        # TODO in addition to
        return (ctx.verb.text, self.visit(ctx.subsetList()), None)

    def visitDurationEnd(self, ctx) -> Duration:
        return Duration(duration_end=ctx.getText())

    def visitDurationSpan(self, ctx) -> Duration:
        return Duration(duration_span=ctx.getText())

demystify_visitor = DemystifyDataVisitor()
