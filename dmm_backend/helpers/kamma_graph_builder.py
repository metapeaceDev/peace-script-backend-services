"""
Kamma-Vipāka Graph Builder

Constructs graph visualization from KammaStorage data.
Implements causality chain detection and graph algorithms.

Author: PeaceScript Team
Date: 6 November 2024
Version: 1.0
"""

import networkx as nx
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from models.kamma_graph import KammaNode, KammaEdge, KammaGraph
from kamma_engine import KammaStorage, KammaRecord, KammaType


class KammaGraphBuilder:
    """
    สร้าง KammaGraph จาก KammaStorage
    
    ใช้ NetworkX เพื่อ graph algorithms (BFS/DFS, shortest path, cycle detection)
    แปลง KammaRecord → KammaNode และหาความสัมพันธ์ → KammaEdge
    
    Attributes:
        storage: KammaStorage ที่เก็บข้อมูลกรรม
        graph_nx: NetworkX DiGraph สำหรับ algorithms
        life_history: ข้อมูลชาติก่อน (สำหรับ life_index mapping)
    
    Examples:
        >>> storage = KammaStorage(character_id="char_123")
        >>> builder = KammaGraphBuilder(storage)
        >>> graph = builder.build_graph(
        ...     model_id="char_123",
        ...     life_range=(-3, 0),  # 3 ชาติก่อน + ปัจจุบัน
        ...     filter_type="kusala"  # เฉพาะกุศลกรรม
        ... )
        >>> print(f"Nodes: {len(graph.nodes)}, Edges: {len(graph.edges)}")
    """
    
    def __init__(
        self,
        storage: KammaStorage,
        life_history: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Initialize graph builder
        
        Args:
            storage: KammaStorage with kamma records
            life_history: List of past lives data (for life_index mapping)
                Format: [
                    {
                        "life_index": -1,
                        "realm": "มนุษย์",
                        "start_date": datetime(...),
                        "end_date": datetime(...)
                    },
                    ...
                ]
        """
        self.storage = storage
        self.life_history = life_history or []
        self.graph_nx = nx.DiGraph()
        
        # Cache for performance
        self._node_cache: Dict[str, KammaNode] = {}
        self._edge_cache: List[KammaEdge] = []
    
    def build_graph(
        self,
        model_id: str,
        life_range: Tuple[int, int] = (-12, 0),
        filter_type: Optional[str] = None,
        include_vipaka: bool = True
    ) -> KammaGraph:
        """
        Main entry point: สร้าง KammaGraph จาก KammaStorage
        
        Args:
            model_id: Character/Model ID
            life_range: ช่วงชาติที่ต้องการดู (min_life, max_life)
                เช่น (-3, 0) = 3 ชาติก่อน + ชาติปัจจุบัน
            filter_type: กรองตาม type (None/"kusala"/"akusala")
            include_vipaka: รวม vipaka nodes ด้วยหรือไม่
        
        Returns:
            KammaGraph พร้อม nodes, edges, และ summary
        
        Process:
            1. Extract nodes from KammaStorage (kamma + vipaka)
            2. Detect causality relationships → edges
            3. Build NetworkX graph for algorithms
            4. Calculate summary statistics
            5. Return complete KammaGraph
        """
        # Step 1: Extract nodes
        nodes = self._extract_nodes(life_range, filter_type, include_vipaka)
        
        # Step 2: Detect edges (causality relationships)
        edges = self._detect_edges(nodes)
        
        # Step 3: Build NetworkX graph (for algorithms)
        self._build_networkx_graph(nodes, edges)
        
        # Step 4: Create KammaGraph
        graph = KammaGraph(
            model_id=model_id,
            nodes=nodes,
            edges=edges
        )
        
        # Step 5: Calculate summary
        graph.update_summary()
        
        return graph
    
    def _extract_nodes(
        self,
        life_range: Tuple[int, int],
        filter_type: Optional[str],
        include_vipaka: bool
    ) -> List[KammaNode]:
        """
        Extract KammaNode list from KammaStorage
        
        Args:
            life_range: (min_life, max_life) tuple
            filter_type: "kusala" / "akusala" / None
            include_vipaka: Include result nodes or not
        
        Returns:
            List of KammaNode
        """
        nodes: List[KammaNode] = []
        min_life, max_life = life_range
        
        # Collect kamma records
        all_records: List[Tuple[KammaRecord, str]] = []
        
        # Active kusala
        if filter_type is None or filter_type == "kusala":
            all_records.extend([
                (record, "kusala")  # Use specific type instead of generic "kamma"
                for record in self.storage.active_kusala
            ])
        
        # Active akusala
        if filter_type is None or filter_type == "akusala":
            all_records.extend([
                (record, "akusala")  # Use specific type instead of generic "kamma"
                for record in self.storage.active_akusala
            ])
        
        # Ripened records (if include_vipaka)
        if include_vipaka:
            if filter_type is None or filter_type == "kusala":
                all_records.extend([
                    (record, "vipaka")
                    for record in self.storage.ripened_kusala
                ])
            
            if filter_type is None or filter_type == "akusala":
                all_records.extend([
                    (record, "vipaka")
                    for record in self.storage.ripened_akusala
                ])
        
        # Convert to KammaNode
        for record, node_type in all_records:
            life_index = self._get_life_index(record.created_at)
            
            # Filter by life_range
            if not (min_life <= life_index <= max_life):
                continue
            
            # Determine realm
            realm = self._get_realm(life_index)
            
            # Create node
            node = KammaNode(
                id=f"node_{record.kamma_id[:8]}",
                type=node_type,  # "kamma" or "vipaka"
                label=record.source_citta_name or "Unknown",
                life_index=life_index,
                date=record.created_at,
                realm=realm,
                weight=record.potency,
                tags=self._generate_tags(record),
                kamma_record_id=record.kamma_id,
                metadata={
                    "timing": str(record.timing),
                    "function": str(record.function),
                    "strength": str(record.strength),
                    "has_ripened": record.has_ripened,
                    "notes": record.notes or ""
                }
            )
            
            nodes.append(node)
            self._node_cache[node.id] = node
        
        return nodes
    
    def _detect_edges(self, nodes: List[KammaNode]) -> List[KammaEdge]:
        """
        Detect causality relationships between nodes
        
        Logic:
        1. Kamma → Vipaka (cause-result): If kamma has ripened, connect to vipaka
        2. Kamma → Kamma (support/obstruct): If two kamma are temporally close
        3. Chronological ordering: Earlier kamma can support/obstruct later kamma
        
        Args:
            nodes: List of KammaNode
        
        Returns:
            List of KammaEdge
        """
        edges: List[KammaEdge] = []
        
        # Group nodes by type
        kamma_nodes = [n for n in nodes if n.type == "kamma"]
        vipaka_nodes = [n for n in nodes if n.type == "vipaka"]
        
        # 1. Kamma → Vipaka edges (cause-result)
        for kamma in kamma_nodes:
            # Check if this kamma has ripened
            if kamma.metadata.get("has_ripened"):
                # Find corresponding vipaka
                kamma_record_id = kamma.kamma_record_id
                
                for vipaka in vipaka_nodes:
                    if vipaka.kamma_record_id == kamma_record_id:
                        edge = KammaEdge(
                            from_node=kamma.id,
                            to_node=vipaka.id,
                            kind="cause",
                            strength=1.0,  # Direct causality = max strength
                            metadata={
                                "relationship": "kamma-vipaka",
                                "confidence": 1.0
                            }
                        )
                        edges.append(edge)
                        break
        
        # 2. Kamma → Kamma edges (support/obstruct)
        # Sort kamma by date
        sorted_kamma = sorted(kamma_nodes, key=lambda n: n.date)
        
        for i, earlier_kamma in enumerate(sorted_kamma):
            for later_kamma in sorted_kamma[i+1:]:
                # Check temporal proximity (within 7 days)
                time_diff = (later_kamma.date - earlier_kamma.date).days
                
                if time_diff > 7:
                    continue
                
                # Determine relationship
                earlier_tags = set(earlier_kamma.tags)
                later_tags = set(later_kamma.tags)
                
                # Support: Same type (kusala ↔ kusala or akusala ↔ akusala)
                if ("kusala" in earlier_tags and "kusala" in later_tags) or \
                   ("akusala" in earlier_tags and "akusala" in later_tags):
                    kind = "support"
                    strength = 0.7 * (1.0 - time_diff / 7.0)  # Decay over time
                
                # Obstruct: Different type (kusala ↔ akusala)
                elif ("kusala" in earlier_tags and "akusala" in later_tags) or \
                     ("akusala" in earlier_tags and "kusala" in later_tags):
                    kind = "obstruct"
                    strength = 0.5 * (1.0 - time_diff / 7.0)
                
                else:
                    continue
                
                edge = KammaEdge(
                    from_node=earlier_kamma.id,
                    to_node=later_kamma.id,
                    kind=kind,
                    strength=strength,
                    metadata={
                        "relationship": "kamma-kamma",
                        "time_diff_days": time_diff
                    }
                )
                edges.append(edge)
        
        self._edge_cache = edges
        return edges
    
    def _build_networkx_graph(self, nodes: List[KammaNode], edges: List[KammaEdge]):
        """
        Build NetworkX DiGraph for graph algorithms
        
        Args:
            nodes: List of KammaNode
            edges: List of KammaEdge
        """
        self.graph_nx.clear()
        
        # Add nodes
        for node in nodes:
            self.graph_nx.add_node(
                node.id,
                type=node.type,
                label=node.label,
                weight=node.weight,
                life_index=node.life_index
            )
        
        # Add edges
        for edge in edges:
            self.graph_nx.add_edge(
                edge.from_node,
                edge.to_node,
                kind=edge.kind,
                strength=edge.strength
            )
    
    def find_causality_chains(
        self,
        start_node_id: str,
        max_depth: int = 5
    ) -> List[List[str]]:
        """
        Find all causality chains starting from a node (BFS)
        
        Args:
            start_node_id: Starting node ID
            max_depth: Maximum chain length
        
        Returns:
            List of chains (each chain is list of node IDs)
            
        Examples:
            >>> chains = builder.find_causality_chains("node_abc123", max_depth=3)
            >>> print(chains)
            [
                ["node_abc123", "node_def456", "node_ghi789"],
                ["node_abc123", "node_xyz999"]
            ]
        """
        if start_node_id not in self.graph_nx:
            return []
        
        chains: List[List[str]] = []
        
        # BFS traversal
        def bfs_chains(node_id: str, path: List[str], depth: int):
            if depth >= max_depth:
                if len(path) > 1:
                    chains.append(path.copy())
                return
            
            # Get successors
            successors = list(self.graph_nx.successors(node_id))
            
            if not successors:
                # Leaf node - save chain
                if len(path) > 1:
                    chains.append(path.copy())
                return
            
            # Explore each successor
            for successor in successors:
                if successor not in path:  # Avoid cycles
                    path.append(successor)
                    bfs_chains(successor, path, depth + 1)
                    path.pop()
        
        bfs_chains(start_node_id, [start_node_id], 0)
        return chains
    
    def search_nodes(
        self,
        query: str = "",
        node_type: Optional[str] = None,
        life_index: Optional[int] = None,
        realm: Optional[str] = None,
        min_weight: Optional[float] = None,
        max_weight: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> List[KammaNode]:
        """
        Search nodes by various criteria
        
        Args:
            query: Search in label (case-insensitive)
            node_type: Filter by type ("kamma"/"vipaka"/"neutral")
            life_index: Filter by specific life
            realm: Filter by realm
            min_weight: Minimum weight threshold
            max_weight: Maximum weight threshold
            tags: Must contain all these tags
        
        Returns:
            List of matching KammaNode
        """
        results: List[KammaNode] = []
        
        for node in self._node_cache.values():
            # Filter by type
            if node_type and node.type != node_type:
                continue
            
            # Filter by life_index
            if life_index is not None and node.life_index != life_index:
                continue
            
            # Filter by realm
            if realm and node.realm != realm:
                continue
            
            # Filter by weight
            if min_weight is not None and node.weight < min_weight:
                continue
            if max_weight is not None and node.weight > max_weight:
                continue
            
            # Filter by tags
            if tags:
                node_tags_set = set(tag.lower() for tag in node.tags)
                required_tags_set = set(tag.lower() for tag in tags)
                if not required_tags_set.issubset(node_tags_set):
                    continue
            
            # Filter by query (label search)
            if query and query.lower() not in node.label.lower():
                continue
            
            results.append(node)
        
        return results
    
    def _get_life_index(self, date: datetime) -> int:
        """
        Determine life_index from date
        
        Uses life_history to map dates to life indices.
        If no history, defaults to 0 (current life).
        
        Args:
            date: Event datetime
        
        Returns:
            life_index (-12 to 0)
        """
        if not self.life_history:
            return 0  # Current life
        
        # Find matching life
        for life in self.life_history:
            start = life.get("start_date")
            end = life.get("end_date")
            
            if start and end:
                if start <= date <= end:
                    return life.get("life_index", 0)
        
        # Default: current life
        return 0
    
    def _get_realm(self, life_index: int) -> str:
        """
        Get realm for a life_index
        
        Args:
            life_index: Life index (-12 to 0)
        
        Returns:
            Realm name (Thai)
        """
        if not self.life_history:
            return "มนุษย์"  # Default: Human realm
        
        for life in self.life_history:
            if life.get("life_index") == life_index:
                return life.get("realm", "มนุษย์")
        
        return "มนุษย์"
    
    def _generate_tags(self, record: KammaRecord) -> List[str]:
        """
        Generate tags for a KammaRecord
        
        Args:
            record: KammaRecord
        
        Returns:
            List of tags
        """
        tags: List[str] = []
        
        # Kamma type
        if record.kamma_type == KammaType.KUSALA:
            tags.append("kusala")
        elif record.kamma_type == KammaType.AKUSALA:
            tags.append("akusala")
        
        # Timing
        tags.append(str(record.timing).split(".")[-1].lower())
        
        # Strength
        tags.append(str(record.strength).split(".")[-1].lower())
        
        # Function
        tags.append(str(record.function).split(".")[-1].lower())
        
        return tags


# Export
__all__ = ["KammaGraphBuilder"]
