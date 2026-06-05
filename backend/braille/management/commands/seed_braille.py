from django.core.management.base import BaseCommand
from braille.models import BrailleCharacter, BrailleSentence

BRAILLE_DATA = [
    ('a', '1', '⠁'), ('b', '12', '⠃'), ('c', '14', '⠉'),
    ('d', '145', '⠙'), ('e', '15', '⠑'), ('f', '124', '⠋'),
    ('g', '1245', '⠛'), ('h', '125', '⠓'), ('i', '24', '⠊'),
    ('j', '245', '⠚'), ('k', '13', '⠅'), ('l', '123', '⠇'),
    ('m', '134', '⠍'), ('n', '1345', '⠝'), ('o', '135', '⠕'),
    ('p', '1234', '⠏'), ('q', '12345', '⠟'), ('r', '1235', '⠗'),
    ('s', '234', '⠎'), ('t', '2345', '⠞'), ('u', '136', '⠥'),
    ('v', '1236', '⠧'), ('w', '2456', '⠺'), ('x', '1346', '⠭'),
    ('y', '13456', '⠽'), ('z', '1356', '⠵'),
]

SAMPLE_SENTENCES = [
    ('hello', '⠓⠑⠇⠇⠕', 1),
    ('world', '⠺⠕⠗⠇⠙', 1),
    ('braille', '⠃⠗⠁⠊⠇⠇⠑', 2),
    ('learning', '⠇⠑⠁⠗⠝⠊⠝⠛', 2),
    ('practice', '⠏⠗⠁⠉⠞⠊⠉⠑', 3),
    ('together', '⠞⠕⠛⠑⠞⠓⠑⠗', 3),
]


class Command(BaseCommand):
    help = '初始化盲文字符数据和示例句子'

    def handle(self, *args, **options):
        created_chars = 0
        for char, dots, unicode_repr in BRAILLE_DATA:
            _, created = BrailleCharacter.objects.get_or_create(
                character=char,
                defaults={
                    'dots': dots,
                    'unicode_repr': unicode_repr,
                    'grade': 1,
                    'description': f'字母 {char.upper()} 的盲文表示，点位: {dots}',
                }
            )
            if created:
                created_chars += 1

        created_sentences = 0
        for text, braille_text, difficulty in SAMPLE_SENTENCES:
            _, created = BrailleSentence.objects.get_or_create(
                text=text,
                defaults={
                    'braille_text': braille_text,
                    'difficulty_level': difficulty,
                }
            )
            if created:
                created_sentences += 1

        self.stdout.write(self.style.SUCCESS(
            f'成功创建 {created_chars} 个盲文字符和 {created_sentences} 个示例句子'
        ))
