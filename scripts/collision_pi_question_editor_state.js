(function attachQuestionEditorState(globalScope) {
  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function draftKey(sectionId) {
    return `collision-pi-question-editor:${sectionId}:draft-v1`;
  }

  function parseStoredDraft(rawDraft) {
    try {
      return rawDraft === null ? null : JSON.parse(rawDraft);
    } catch {
      return null;
    }
  }

  function isMatchingBank(candidate, original) {
    const originalQuota = original?.question_count_by_node;
    const candidateQuota = candidate?.question_count_by_node;
    if (
      candidate?.course_id !== original?.course_id ||
      candidate?.section_id !== original?.section_id ||
      candidate?.version !== original?.version ||
      !Array.isArray(candidate?.questions) ||
      !Array.isArray(original?.questions) ||
      !candidateQuota ||
      typeof candidateQuota !== 'object'
    ) return false;

    const originalNodeIds = Object.keys(originalQuota);
    if (
      Object.keys(candidateQuota).length !== originalNodeIds.length ||
      !originalNodeIds.every(nodeId => candidateQuota[nodeId] === originalQuota[nodeId]) ||
      candidate.questions.length !== original.questions.length
    ) return false;

    const canonicalById = new Map(original.questions.map(question => [question.id, question]));
    const candidateIds = candidate.questions.map(question => question?.id);
    return new Set(candidateIds).size === candidateIds.length && candidate.questions.every(question => {
      const canonical = canonicalById.get(question?.id);
      return canonical && question.node_id === canonical.node_id;
    });
  }

  function loadDraft({ sectionId, banks, getItem, setItem }) {
    const original = banks[sectionId];
    const qualifiedRaw = getItem(draftKey(sectionId));
    const saved = parseStoredDraft(qualifiedRaw);
    if (isMatchingBank(saved, original)) return saved;
    if (sectionId === 'A' && qualifiedRaw === null) {
      const legacy = parseStoredDraft(getItem('collision-pi-a-question-draft'));
      if (isMatchingBank(legacy, original)) {
        setItem(draftKey(sectionId), JSON.stringify(legacy));
        return legacy;
      }
    }
    return clone(original);
  }

  function nodeActionState(nodeId) {
    const disableNodeOnlyActions = nodeId === 'all';
    return {
      disableNodeOnlyActions,
      canApplyNodeAction: !disableNodeOnlyActions
    };
  }

  function nodeQuestionIds(nodeId, questions) {
    if (!nodeActionState(nodeId).canApplyNodeAction) return [];
    return questions.filter(question => question.node_id === nodeId).map(question => question.id);
  }

  function moveNodeId(currentNodeId, nodes, step) {
    if (!nodes.length) return '';
    if (currentNodeId === 'all') return step > 0 ? nodes[0] : nodes[nodes.length - 1];
    const currentIndex = nodes.indexOf(currentNodeId);
    const index = currentIndex < 0 ? 0 : currentIndex;
    return nodes[(index + step + nodes.length) % nodes.length];
  }

  const api = { draftKey, isMatchingBank, loadDraft, nodeActionState, nodeQuestionIds, moveNodeId };
  if (typeof module === 'object' && module.exports) module.exports = api;
  globalScope.CollisionPiQuestionEditorState = api;
})(typeof window === 'undefined' ? globalThis : window);
