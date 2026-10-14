"""Exit checks for an Appendix A node file."""

from graphrag_poc.models import Node, NodeType


def validate_nodes(nodes: list[Node], pages: list[int]) -> list[str]:
    """Return human-readable errors. An empty list means the file passes."""

    errors: list[str] = []
    ids = [node.node_id for node in nodes]
    id_set = set(ids)
    if len(id_set) != len(ids):
        errors.append("duplicate node_id values")
    by_id = {node.node_id: node for node in nodes}

    covered: set[int] = set()
    for node in nodes:
        try:
            Node.model_validate(node.model_dump())
        except ValueError as exc:
            errors.append(f"{node.node_id}: {exc}")
            continue
        if node.parent is not None and node.parent not in id_set:
            errors.append(f"{node.node_id}: parent {node.parent} does not exist")
        for label, values in (
            ("siblings", node.siblings),
            ("references", node.references),
        ):
            missing = [value for value in values if value not in id_set]
            if missing:
                errors.append(f"{node.node_id}: {label} missing {missing}")
        for caution_id in node.bound_cautions:
            caution = by_id.get(caution_id)
            if caution is None:
                errors.append(f"{node.node_id}: bound caution {caution_id} does not exist")
            elif caution.type is not NodeType.CAUTION:
                errors.append(f"{node.node_id}: {caution_id} is not a caution")
        if node.type is NodeType.BOILERPLATE:
            covered.update(range(node.page_start, node.page_end + 1))
        covered.update(element.page for element in node.elements)

    missing_pages = [page for page in pages if page not in covered]
    if missing_pages:
        preview = ", ".join(str(page) for page in missing_pages[:12])
        errors.append(f"{len(missing_pages)} pages have no node: {preview}")
    return errors
