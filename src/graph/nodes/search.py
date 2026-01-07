from graph.state import PipelineSentence


async def search_node(sentence: PipelineSentence) -> PipelineSentence:
    """
    [MOCK]
    검색(Search)을 수행하는 노드입니다.
    """

    # 1. retry_count 증가 (재검색인 경우)
    # workflow.py에서 초기화된 retry_count를 확인
    if "retry_count" in sentence:
        # 이 노드가 호출되었다는 것은, 처음이거나 재시도 중이라는 뜻.
        # 재시도 횟수를 여기서 증가시키면 다음 Verification 단계에서 확인 가능.
        # 단, 첫 진입(Extraction 후)에는 0이어야 하는데,
        # Loop를 돌아서 다시 Search로 오면 증가시켜야 함.
        # 하지만 Graph 구조상 Search 노드는 매번 실행됨.
        # 따라서 "Search 실행 횟수"를 세는 것이 됨.
        # 검증 로직에서는 "이전까지의 시도 횟수"를 봐야 하므로,
        # 검증 실패 후 다시 Search로 올 때 증가되어 있어야 함.
        # 방법: 검증 실패 시 Conditional Edge에서 바로 Search로 보내는데,
        # 이 때 상태를 변경할 수 없으므로, Search 노드 진입 시에
        # "이게 재시도인가?"를 알아야 함.
        # 판별법: sources가 이미 채워져 있으면 재시도임. (처음엔 비어있음)
        if "sources" in sentence and sentence["sources"]:
            sentence["retry_count"] += 1

    # 2. 검색 수행 (Mock)
    # ... 실제 검색 API 호출 (비동기) ...
    # 재검색 시 다른 검색어를 사용하거나 결과를 다르게 할 수 있음
    sentence["sources"] = [
        {
            "title": "Trusted Source A",
            "url": "https://example.com/a",
            "snippet": f"This supports the claim X... (Retry: {sentence.get('retry_count', 0)})",
        }
    ]

    # 순수 검색 노드이므로 검증 로직 호출 제거
    return sentence
