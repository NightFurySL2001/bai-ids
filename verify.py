import regex

# Using atomic groups to prevent catastrophic backtracking where possible
pattern = r"""(?x)
(?(DEFINE)
(?<IDS_Definition_Row>
    (?&Ideograph_Char)(?&TAB)(?&IDS_Locale_Definition)
    (?:(?&TAB)(?&IDS_Alternative_Definition))?
)
(?<IDS_Locale_Definition>(?&IDS_Sequence)|(?&IDS_Locale_Sequence)(?:;(?&IDS_Locale_Sequence))*)
(?<IDS_Alternative_Definition>
    (?:(?&IDS_Sequence)|(?&IDS_Locale_Sequence))
    (?:;(?:(?&IDS_Sequence)|(?&IDS_Locale_Sequence)))*
)
(?<IDS_Locale_Sequence>(?&Unique_Sequence_Separator)?(?&IDS_Sequence)(?&Variant_Identifier_Definition)?)
(?<IDS_Sequence>
     (?&Stroke_Chain)
 |
     (?&IDS_UnaryOperator)(?&IDS_Component)
 |
     (?&IDS_BinaryOperator)(?&IDS_Component)(?&IDS_Component)
 |
     (?&IDS_BinaryOverlapOperator)(?&Overlap_Modifier)(?&IDS_Component)(?&IDS_Component)
 |
     (?&IDS_BinaryAmbiguousOperator)(?&Index_Modifier)(?&IDS_Component)(?&IDS_Component)
 |
     (?&IDS_TrinaryOperator)(?&IDS_Component)(?&IDS_Component)(?&IDS_Component)
)
(?<IDS_Component>(?&IDS_Sequence)|(?&Stroke_Chain)|(?&Ideo_with_Variant_ID)|(?&Curves)|[リ〢〣コ])
(?<Ideo_with_Variant_ID>(?&Ideograph_Char_with_Variant)(?&Variant_Identifier)?)
(?<Variant_Identifier_Definition>\((?&Variant_Identifier)(?:,(?&Variant_Identifier))*\))
(?<Variant_Identifier>(?&Wildcard_Source)|(?&Unicode_Sources)|(?&UCV_Full_Position)|(?&Imaginary_UCV)|(?&Alternate_Variants))
(?<Wildcard_Source>\.)
(?<Unicode_Sources>[BGHJKMPSTUVQ])
(?<UCV_Full_Position>[qpxy](?&UCV_ID_Number)(?&UCV_Position_Number))
(?<UCV_ID_Number>(?&Three_Digit_Number)[a-z]?)
(?<UCV_Position_Number>(?:(?&Positive_Numeral)|(?&Two_Digit_Number))[xy]?)
(?<Imaginary_UCV>qq(?&UCV_ID_Number)+)
(?<Alternate_Variants>[0-9a-z.]+)
(?<Overlap_Modifier>\[(?&Overlap_Matrix)(?:\|(?&Overlap_Matrix))?\])
(?<Overlap_Matrix>(?&Overlap_Horizontal_Indexing)|(?&Overlap_Rows)|(?&Overlap_Cell)+)
(?<Overlap_Horizontal_Indexing>(?:(?&Number)|(?&Negative_Number))?\:(?:(?&Number)|(?&Negative_Number))?)
(?<Overlap_Rows>(?&Overlap_Row)?(?:,(?&Overlap_Row)?)+)
(?<Overlap_Row>(?&Overlap_Cell)*)
(?<Overlap_Cell>(?&Overlap_Identity)|(?&Overlap_Crossing)|(?&Overlap_Non_Crossing))
(?<Overlap_Identity>[._])
(?<Overlap_Crossing>[xabcd])
(?<Overlap_Non_Crossing>[lr])
(?<Index_Modifier>\[(?&Number)\])
(?<Stroke_Chain>\#\((?&Stroke_Part)+z?\))
(?<Stroke_Part>(?&StReversed_Indicator)?(?:(?&Ideograph_Char)|(?&Stroke_Letter))(?:(?&StCrossing_Indicator)|(?&StBreak_Indicator))?)
(?<Stroke_Letter>[HSPN]g?|[SP]Hwg?|[DTJZ]|Wg|Q[abcd])
(?<StReversed_Indicator>\-)
(?<StCrossing_Indicator>x(?&Number))
(?<StBreak_Indicator>b)
(?<Unique_Sequence_Separator>\{(?:\?(?&One_Digit_Number)?)?(?&Ideograph_Char_with_Variant)(?&Unicode_Sources)?\})
(?<Ideograph_Char>(?&Ideograph_Char_with_Variant)|(?&Curves)|[リ〢〣コ])
(?<Ideograph_Char_with_Variant>(?&Hanzi)|(?&CJK_Stroke)|[ユス])
(?<Hanzi>[\p{IsIdeographic}\p{Radical}])
(?<Curves>[◝◞◟◜])
(?<CJK_Stroke>[\u31C0-\u31E3])
(?<TAB>\x09)
(?<IDS_UnaryOperator>[⿾⿿])
(?<IDS_BinaryUniqueOperator>[⿰⿱⿸⿹⿺⿽])
(?<IDS_BinaryOverlapOperator>⿻)
(?<IDS_BinaryAmbiguousOperator>[⿴⿵⿶⿷⿼㇯])
(?<IDS_BinaryOperator>(?&IDS_BinaryUniqueOperator)|(?&IDS_BinaryOverlapOperator)|(?&IDS_BinaryAmbiguousOperator))
(?<IDS_TrinaryOperator>[⿲⿳])
(?<Positive_Numeral>[1-9])
(?<One_Digit_Number>0|(?&Positive_Numeral))
(?<Two_Digit_Number>(?&One_Digit_Number)(?&One_Digit_Number))
(?<Three_Digit_Number>(?&One_Digit_Number)(?&One_Digit_Number)(?&One_Digit_Number))
(?<Number>0|(?&Positive_Numeral)(?&One_Digit_Number)*)
(?<Negative_Number>\-(?&Positive_Numeral)(?&One_Digit_Number)*)
)
^(?&IDS_Definition_Row)$
"""


print("Compiling regex...")

try:
    regex.DEFAULT_VERSION = regex.V1
    PAT = regex.compile(pattern)
except Exception as e:
    print("Regex compilation failed:", e)
    raise e

print("Regex compiled.")


def test(file_path):
    print(f"\n================\nTesting file: {file_path}")

    total = 0
    match_count = 0
    fails = []

    with open(file_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            total += 1
            line = line.rstrip("\n")

            try:
                # Add timeout to avoid hanging forever
                is_match = PAT.match(line, timeout=0.1)

                if is_match:
                    match_count += 1
                else:
                    fails.append((total, line, "Failed match"))
            except TimeoutError:
                fails.append((total, line, "Timeout (catastrophic backtracking)"))

            if total % 1000 == 0:
                print(f"Processed {total} lines...")

    print(f"\nTested file: {file_path}")
    print(f"Total lines: {total}")
    print(f"Matched IDS_Definition_Row : {match_count}")
    print(f"Failed                     : {total - match_count}")
    print("-" * 40)
    for num, fail_line, reason in fails:
        print(f"Line {num} {reason}: {fail_line}")


if __name__ == "__main__":
    test("ids/ids_lv0.txt")
    test("ids/ids_lv1.txt")
    test("ids/ids_lv2.txt")
