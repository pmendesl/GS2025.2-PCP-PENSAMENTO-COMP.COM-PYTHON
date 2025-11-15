import json
from typing import Dict, List, Tuple, Any
from pathlib import Path

DB_FILE = Path("profiles.json")

class Profile:
    """
    Representa um perfil profissional (usuário/aluno).
    technical_skills e behavioral_skills são dicionários {skill_name: nivel(0-5)}
    """
    def _init_(self, name: str,
                 technical_skills: Dict[str, int] = None,
                 behavioral_skills: Dict[str, int] = None,
                 notes: str = ""):
        self.name = name
        self.technical_skills = technical_skills or {}
        self.behavioral_skills = behavioral_skills or {}
        self.notes = notes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "technical_skills": self.technical_skills,
            "behavioral_skills": self.behavioral_skills,
            "notes": self.notes
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Profile":
        return Profile(
            name=d["name"],
            technical_skills=d.get("technical_skills", {}),
            behavioral_skills=d.get("behavioral_skills", {}),
            notes=d.get("notes", "")
        )

    def _repr_(self):
        return f"<Profile {self.name}>"


class Career:
    """
    Define uma carreira / área. Cada carreira tem requisitos técnicos e comportamentais,
    com pesos (importância).
    requirements_tech: dict(skill -> desired_level 0-5)
    requirements_beh: dict(skill -> desired_level 0-5)
    """
    def _init_(self, title: str,
                 requirements_tech: Dict[str, int],
                 requirements_beh: Dict[str, int],
                 description: str = ""):
        self.title = title
        self.requirements_tech = requirements_tech
        self.requirements_beh = requirements_beh
        self.description = description

    def to_dict(self):
        return {
            "title": self.title,
            "requirements_tech": self.requirements_tech,
            "requirements_beh": self.requirements_beh,
            "description": self.description
        }

    def _repr_(self):
        return f"<Career {self.title}>"


class ProfileDB:
    """Banco simples baseado em JSON para perfis"""
    def _init_(self, filepath: Path = DB_FILE):
        self.filepath = filepath
        self.profiles: List[Profile] = []
        self.load()

    def load(self):
        if not self.filepath.exists():
            self.profiles = []
            return
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.profiles = [Profile.from_dict(p) for p in data]

    def save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([p.to_dict() for p in self.profiles], f, ensure_ascii=False, indent=2)

    def add_profile(self, profile: Profile):
        self.profiles.append(profile)
        self.save()

    def find(self, name: str) -> Profile:
        for p in self.profiles:
            if p.name.lower() == name.lower():
                return p
        return None

    def list_names(self) -> List[str]:
        return [p.name for p in self.profiles]


class Recommender:
    """
    Motor de recomendações:
    - Calcula compatibilidade entre perfil e cada carreira
    - Gera recomendações de melhoria (ácidos)
    """
    def _init_(self, careers: List[Career]):
        self.careers = careers

    @staticmethod
    def _skill_score(profile_level: int, required_level: int) -> float:
        """
        Score por habilidade:
        - se profile>=required => 1.0 (atingiu)
        - se profile<required => profile/required (proporcional)
        """
        if required_level <= 0:
            return 1.0
        return min(1.0, profile_level / required_level)

    def compatibility(self, profile: Profile, career: Career) -> float:
        """Retorna compatibilidade agregada 0..1 entre profile e career"""
        tech_scores = []
        for skill, req in career.requirements_tech.items():
            lvl = profile.technical_skills.get(skill, 0)
            tech_scores.append(self._skill_score(lvl, req))
        beh_scores = []
        for skill, req in career.requirements_beh.items():
            lvl = profile.behavioral_skills.get(skill, 0)
            beh_scores.append(self._skill_score(lvl, req))

        # médias simples; ponderar para dar importância maior a técnicas por exemplo
        tech_avg = sum(tech_scores) / len(tech_scores) if tech_scores else 1.0
        beh_avg = sum(beh_scores) / len(beh_scores) if beh_scores else 1.0

        # ponderação: 70% técnica, 30% comportamental (ajustável)
        overall = 0.7 * tech_avg + 0.3 * beh_avg
        return overall

    def recommend(self, profile: Profile, top_n: int = 3) -> List[Tuple[Career, float]]:
        """Retorna top_n carreiras ordenadas por compatibilidade decrescente"""
        scored = [(career, self.compatibility(profile, career)) for career in self.careers]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_n]

    def improvement_areas(self, profile: Profile, career: Career, top_n: int = 5) -> List[Tuple[str, float, int]]:
        """
        Retorna as top_n habilidades onde o profile mais "falha" em relação à carreira.
        Cada item: (skill_name, gap_ratio, required_level)
        gap_ratio: 1 - (profile_level / required_level)  (0 = ok, mais próximo de 1 = maior gap)
        """
        gaps = []
        for skill, req in career.requirements_tech.items():
            lvl = profile.technical_skills.get(skill, 0)
            if req > 0:
                gap = max(0.0, 1.0 - (lvl / req))
                if gap > 0:
                    gaps.append((skill + " (técnica)", gap, req))
        for skill, req in career.requirements_beh.items():
            lvl = profile.behavioral_skills.get(skill, 0)
            if req > 0:
                gap = max(0.0, 1.0 - (lvl / req))
                if gap > 0:
                    gaps.append((skill + " (comportamental)", gap, req))
        gaps.sort(key=lambda x: x[1], reverse=True)
        return gaps[:top_n]


# --- Carreiras pré-definidas (exemplo) ---
def default_careers() -> List[Career]:
    """
    Cada requisito é um inteiro 0..5 que indica o nível desejado.
    Ajuste conforme necessário para sua disciplina/objetivos.
    """
    return [
        Career(
            title="Desenvolvedor de Software",
            requirements_tech={"Python": 4, "Estruturas de Dados": 4, "Banco de Dados": 3, "Controle de Versão (git)": 3},
            requirements_beh={"Trabalho em Equipe": 4, "Comunicação": 3, "Resolução de Problemas": 4},
            description="Criação de aplicações, APIs e sistemas backend/frontend."
        ),
        Career(
            title="Cientista de Dados",
            requirements_tech={"Python": 4, "Estatística": 4, "Manipulação de Dados (pandas)": 4, "Machine Learning": 3},
            requirements_beh={"Curiosidade": 5, "Resolução de Problemas": 4, "Comunicação": 3},
            description="Análise de dados, modelagem e insights para tomada de decisão."
        ),
        Career(
            title="Engenheiro de Automação / Embutidos",
            requirements_tech={"C": 4, "Eletrônica": 4, "Microcontroladores (Arduino/MCU)": 4, "Projeto de Circuitos": 3},
            requirements_beh={"Atenção a Detalhes": 4, "Trabalho em Equipe": 3, "Resiliência": 3},
            description="Desenvolvimento de sistemas embarcados e automação."
        ),
        Career(
            title="Analista de QA / Testes",
            requirements_tech={"Testes Automatizados": 4, "Python": 3, "CI/CD": 3, "Documentação Técnica": 3},
            requirements_beh={"Atenção a Detalhes": 5, "Comunicação": 4},
            description="Garantia de qualidade, automação de testes e revisão de funcionalidades."
        ),
    ]


# --- Interface de Linha de Comando Simples ---
def prompt_skill_input(skills_list: List[str]) -> Dict[str, int]:
    """
    Pede ao usuário um nível para cada skill na lista.
    Nível 0..5
    """
    out = {}
    for s in skills_list:
        while True:
            val = input(f"Nível para '{s}' (0-5, ENTER=0): ").strip()
            if val == "":
                val = "0"
            if val.isdigit():
                v = int(val)
                if 0 <= v <= 5:
                    out[s] = v
                    break
            print("Entrada inválida. Informe um inteiro entre 0 e 5.")
    return out


def union_skills(careers: List[Career]) -> Tuple[List[str], List[str]]:
    tech = set()
    beh = set()
    for c in careers:
        tech.update(c.requirements_tech.keys())
        beh.update(c.requirements_beh.keys())
    return sorted(tech), sorted(beh)


def main_cli():
    db = ProfileDB()
    careers = default_careers()
    recommender = Recommender(careers)

    print("=== Sistema de Orientação Profissional (Python) ===")
    while True:
        print("\nEscolha uma opção:")
        print("1) Cadastrar novo perfil")
        print("2) Listar perfis")
        print("3) Analisar perfil e gerar recomendações")
        print("4) Mostrar perfil salvo")
        print("5) Sair")
        choice = input("> ").strip()
        if choice == "1":
            name = input("Nome do perfil: ").strip()
            tech_skills_all, beh_skills_all = union_skills(careers)
            print("\nPreencha suas habilidades técnicas:")
            tech = prompt_skill_input(tech_skills_all)
            print("\nPreencha suas habilidades comportamentais:")
            beh = prompt_skill_input(beh_skills_all)
            notes = input("Observações (opcional): ").strip()
            profile = Profile(name=name, technical_skills=tech, behavioral_skills=beh, notes=notes)
            db.add_profile(profile)
            print(f"Perfil '{name}' cadastrado com sucesso.")
        elif choice == "2":
            names = db.list_names()
            if not names:
                print("Nenhum perfil cadastrado.")
            else:
                print("Perfis cadastrados:")
                for n in names:
                    print(" -", n)
        elif choice == "3":
            name = input("Nome do perfil a analisar: ").strip()
            profile = db.find(name)
            if not profile:
                print("Perfil não encontrado. Cadastre-o primeiro.")
                continue
            print(f"\nAnalisando perfil: {profile.name}\n")
            recs = recommender.recommend(profile, top_n=3)
            for idx, (career, score) in enumerate(recs, start=1):
                pct = round(score * 100, 1)
                print(f"{idx}) {career.title} — compatibilidade: {pct}%")
                print(f"   Descrição: {career.description}")
                gaps = recommender.improvement_areas(profile, career, top_n=5)
                if gaps:
                    print("   Principais áreas para aprimorar:")
                    for gskill, gap, req in gaps:
                        gap_pct = round(gap * 100, 1)
                        print(f"     - {gskill}: gap {gap_pct}% (nível requerido: {req})")
                else:
                    print("   Nenhuma área crítica para aprimorar — ótimo!")
                print()
            save_report = input("Deseja salvar o relatório em JSON? (s/N): ").strip().lower()
            if save_report == "s":
                report = {
                    "profile": profile.to_dict(),
                    "recommendations": [
                        {"career": c.title, "score": s, "description": c.description} for c, s in recs
                    ]
                }
                out_file = Path(f"report_{profile.name.replace(' ', '_')}.json")
                with open(out_file, "w", encoding="utf-8") as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
                print("Relatório salvo em", out_file)
        elif choice == "4":
            name = input("Nome do perfil: ").strip()
            profile = db.find(name)
            if not profile:
                print("Perfil não encontrado.")
            else:
                print(json.dumps(profile.to_dict(), ensure_ascii=False, indent=2))
        elif choice == "5":
            print("Saindo. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")


if "_name_" == "_main_":
  main_cli()
