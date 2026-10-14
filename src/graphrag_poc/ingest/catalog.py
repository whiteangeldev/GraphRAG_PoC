"""Approved corpus, one entry per document in the corpus register."""

from dataclasses import dataclass
from pathlib import Path

from graphrag_poc.models import DocType

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "data" / "corpus" / "source"
NODES = ROOT / "data" / "nodes"


@dataclass(frozen=True)
class DocumentSpec:
    """One approved PDF and the node-file fields that are constant for it."""

    doc_key: str
    filename: str
    lang: str
    doc_type: DocType
    edition: str
    title: str
    series: tuple[str, ...]

    @property
    def path(self) -> Path:
        return SOURCE / self.filename


DOCUMENTS: tuple[DocumentSpec, ...] = (
    DocumentSpec(
        doc_key="tm280_10",
        filename="TM-9-2320-280-10.pdf",
        lang="en",
        doc_type=DocType.OPERATION,
        edition="Change 2, 30 November 2001",
        title="Operator's Manual, M998 series",
        series=("M998",),
    ),
    DocumentSpec(
        doc_key="tm280_20_2",
        filename="TM-9-2320-280-20-2.pdf",
        lang="en",
        doc_type=DocType.MAINTENANCE,
        edition="Supersedes 19 January 1990",
        title="Unit Maintenance, Volume 2",
        series=("M998",),
    ),
    DocumentSpec(
        doc_key="tm280_20_1",
        filename="TM-9-2320-280-20-1.pdf",
        lang="en",
        doc_type=DocType.CODE_REFERENCE,
        edition="Supersedes 19 January 1990",
        title="Unit Maintenance, Volume 1, troubleshooting",
        series=("M998",),
    ),
    DocumentSpec(
        doc_key="tm280_24p_1",
        filename="TM-9-2320-280-24P-1.pdf",
        lang="en",
        doc_type=DocType.PARTS,
        edition="Change 2, supersedes 31 January 1996",
        title="Repair Parts and Special Tools List, Volume 1",
        series=("M998",),
    ),
    DocumentSpec(
        doc_key="tm2815_34",
        filename="TM-9-2815-237-34.pdf",
        lang="en",
        doc_type=DocType.MAINTENANCE,
        edition="January 1996",
        title="6.2 L and 6.5 L diesel engine maintenance",
        series=("6.2L", "6.5L"),
    ),
    DocumentSpec(
        doc_key="mlit_b052",
        filename="mlit-b052.pdf",
        lang="ja",
        doc_type=DocType.OTHER,
        edition="2025.9.26",
        title="灯火器及び反射器並びに指示装置の取付装置の技術基準",
        series=(),
    ),
)

BY_KEY = {spec.doc_key: spec for spec in DOCUMENTS}
