import os
import re
from io import StringIO

from antlr4 import Utils
from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.Parser import Parser
from antlr4.ParserRuleContext import ParserRuleContext
from antlr4.StdinStream import InputStream
from antlr4.atn.PredictionMode import PredictionMode
from antlr4.error.ErrorStrategy import BailErrorStrategy
from antlr4.error.ErrorListener import ConsoleErrorListener
from antlr4.error.Errors import ParseCancellationException
from antlr4.tree.Tree import TerminalNode
from antlr4.tree.Trees import Trees

from grammar.DemystifyLexer import DemystifyLexer
from grammar.DemystifyParser import DemystifyParser
from mtg_types import Ability

def parse(rule: str, text: str):
    lexer = DemystifyLexer(InputStream(text))
    lexer.removeErrorListener(ConsoleErrorListener.INSTANCE)
    stream = CommonTokenStream(lexer)
    try:
        parser = DemystifyParser(stream)
        parser._interp.predictionMode = PredictionMode.SLL
        parser._errHandler = BailErrorStrategy()
        parser.removeErrorListener(ConsoleErrorListener.INSTANCE)
        return getattr(parser, rule)()
    except ParseCancellationException:
        parser = DemystifyParser(stream)
        parser._errHandler = BailErrorStrategy()
        parser.removeErrorListener(ConsoleErrorListener.INSTANCE)
        return getattr(parser, rule)()

def print_lex(text: str):
    lexer = DemystifyLexer(InputStream(text))
    stream = CommonTokenStream(lexer)
    stream.fill()
    for token in stream.tokens:
        print('%s: %s' % (token.text, DemystifyLexer.symbolicNames[token.type]))

# Pretty printing
# Based on the pretty printing code of SnippetsTest (Java)
# https://github.com/grosenberg/SnippetsTest/blob/master/src/test/java/net/certiv/remark/test/TreeUtils.java
def to_pretty_tree(tree: ParserRuleContext, ruleNames: list[str] = None, recog: Parser = None) -> str:
    eol = os.linesep
    indent = '  '

    def lead(level: int) -> str:
        if level > 0:
            return eol + (level*indent)
        else:
            return ''

    def process(tree: ParserRuleContext, level: int, ruleNames: list[str] = None, recog: Parser = None) -> str:
        s = Utils.escapeWhitespace(Trees.getNodeText(tree, ruleNames=ruleNames, recog=recog), False)
        sb = StringIO()
        sb.write(lead(level))
        if isinstance(tree, TerminalNode):
            sb.write('"')
            sb.write(s)
            sb.write('"')
        else:
            sb.write(s)
            sb.write(' ')
            for child in tree.children:
                sb.write(process(child, level+1, ruleNames, recog))
        return sb.getvalue()

    return re.sub(r'(?m)^\\s+$', '',
        re.sub(r'\\r?\\n\\r?\\n', eol,
        process(tree, 0, ruleNames, recog)))

def pretty_tree(rule: str, text: str):
    lexer = DemystifyLexer(InputStream(text))
    stream = CommonTokenStream(lexer)
    try:
        parser = DemystifyParser(stream)
        parser._interp.predictionMode = PredictionMode.SLL
        parser._errHandler = BailErrorStrategy()
        tree = getattr(parser, rule)()
    except ParseCancellationException:
        parser = DemystifyParser(stream)
        tree = getattr(parser, rule)()
    return to_pretty_tree(tree, recog=parser)
