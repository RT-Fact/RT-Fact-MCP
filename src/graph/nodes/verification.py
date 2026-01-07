from graph.state import PipelineSentence


async def verification_node(sentence: PipelineSentence) -> PipelineSentence:
    """
    [Logic]
    단일 문장(PipelineSentence)과 소스(Sources)를 바탕으로 진실 여부를 판정합니다.
    """

    # ... 실제 검증 API 호출 ...

    # PipelineSentence 구조에 맞춰 결과 업데이트
    # 재검색 루프 테스트를 위해 특정 조건에서 FALSE 반환하도록 Mocking 가능
    # 여기서는 retry_count가 0이면 FALSE, 1이상이면 TRUE로 하여 루프 동작 확인

    if sentence.get("retry_count", 0) == 0:
        sentence["verdict"] = "FALSE"
        sentence["suggestion"] = "Need more evidence."
    else:
        sentence["verdict"] = "TRUE"
        sentence["suggestion"] = None

    return sentence
