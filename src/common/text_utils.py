"""텍스트 처리를 위한 공통 유틸리티 모듈"""


def normalize_text(text: str) -> str:
    """
    텍스트 정규화: 공백 제거 및 소문자 변환
    비교(Matching)를 위한 표준 형태로 만듭니다.
    """
    return "".join(text.split()).lower()


def find_fuzzy_indices(original: str, target: str, start_offset: int = 0) -> tuple[int, int]:
    """
    원본 텍스트(original) 내에서 타겟 텍스트(target)의 위치를 "유연하게" 찾습니다.

    특징:
    - 공백(띄어쓰기, 탭, 줄바꿈)과 대소문자를 무시하고 매칭합니다.
    - 매칭된 구간의 '원본' 인덱스(Start, End)를 반환합니다.

    Args:
        original: 원본 텍스트
        target: 찾고자 하는 텍스트 (부분 문자열)
        start_offset: 검색 시작 위치 (기본값 0)

    Returns:
        (start_index, end_index): 매칭된 구간의 시작과 끝 인덱스.
        실패 시 (-1, -1) 반환.
    """
    if not target:
        return -1, -1

    target_clean = normalize_text(target)
    if not target_clean:
        return -1, -1

    target_len = len(target_clean)
    original_len = len(original)
    current_match_count = 0
    match_start_index = -1

    for i in range(start_offset, original_len):
        char = original[i]

        if char.isspace():
            continue

        char_lower = char.lower()

        if char_lower == target_clean[current_match_count]:
            if current_match_count == 0:
                match_start_index = i

            current_match_count += 1

            if current_match_count == target_len:
                return match_start_index, i + 1
        else:
            if current_match_count > 0:
                pass

    return _find_fuzzy_indices_mapping(original, target_clean, start_offset)


def _find_fuzzy_indices_mapping(
    original: str, target_clean: str, start_offset: int
) -> tuple[int, int]:
    """
    내부 구현용: Mapping 테이블 방식
    Original의 (Clean Index -> Original Index) 매핑을 생성하여 정확한 위치 찾기
    """
    clean_to_original_map = []

    for i in range(start_offset, len(original)):
        char = original[i]
        if not char.isspace():
            clean_to_original_map.append(i)

    original_clean = "".join(original[idx].lower() for idx in clean_to_original_map)
    clean_start = original_clean.find(target_clean)

    if clean_start == -1:
        return -1, -1

    clean_end = clean_start + len(target_clean) - 1

    original_start_index = clean_to_original_map[clean_start]
    original_end_index = clean_to_original_map[clean_end] + 1

    return original_start_index, original_end_index
