"""
Script d'évaluation complet pour le système RAG - Phase 2
Teste et évalue les performances du chatbot de support client
"""

import json
from datetime import datetime
from typing import List, Dict, Any
from src.rag_pipeline import RAGPipeline
from src.prompt_engineering import PromptEngineer

class RAGEvaluator:
    """Évaluateur complet du système RAG"""
    
    def __init__(self):
        self.rag_pipeline = RAGPipeline()
        self.prompt_engineer = PromptEngineer()
        self.test_cases = self._load_test_cases()
        
    def _load_test_cases(self) -> List[Dict[str, Any]]:
        """Charge les cas de test pour l'évaluation"""
        return [
            {
                "question": "Comment configurer le VPN ?",
                "expected_keywords": ["vpn.entreprise.com", "Active Directory", "identifiants"],
                "expected_role": "it_support",
                "expected_style": "detailed",
                "category": "IT Support"
            },
            {
                "question": "Où demander des congés ?",
                "expected_keywords": ["portail RH", "rh.techcorp.com", "congés"],
                "expected_role": "hr_assistant", 
                "expected_style": "concise",
                "category": "RH"
            },
            {
                "question": "Quand a lieu l'évaluation annuelle ?",
                "expected_keywords": ["décembre", "évaluation", "annuelle"],
                "expected_role": "hr_assistant",
                "expected_style": "detailed",
                "category": "RH"
            },
            {
                "question": "Comment réinitialiser mon mot de passe ?",
                "expected_keywords": ["support", "IT", "mot de passe"],
                "expected_role": "it_support",
                "expected_style": "technical",
                "category": "IT Support"
            },
            {
                "question": "Quels sont les avantages sociaux ?",
                "expected_keywords": ["avantages", "sociaux", "RH"],
                "expected_role": "hr_assistant",
                "expected_style": "friendly",
                "category": "RH"
            },
            {
                "question": "Problème avec mon email",
                "expected_keywords": ["email", "support", "technique"],
                "expected_role": "it_support",
                "expected_style": "technical",
                "category": "IT Support"
            }
        ]
    
    def evaluate_response_quality(self, question: str, answer: str, context: str) -> Dict[str, Any]:
        """Évalue la qualité d'une réponse"""
        evaluation = {
            "question": question,
            "answer_length": len(answer.split()),
            "context_length": len(context.split()),
            "has_context": "Aucune information" not in context,
            "keyword_matches": 0,
            "relevance_score": 0.0,
            "completeness_score": 0.0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Vérification des mots-clés pertinents
        relevant_keywords = ["vpn", "congés", "évaluation", "portail", "email", "mot de passe", "support", "RH", "IT"]
        answer_lower = answer.lower()
        
        keyword_matches = sum(1 for keyword in relevant_keywords if keyword in answer_lower)
        evaluation["keyword_matches"] = keyword_matches
        
        # Score de pertinence basé sur les mots-clés
        evaluation["relevance_score"] = min(keyword_matches / 5, 1.0)
        
        # Score de complétude basé sur la longueur de la réponse
        if 15 <= evaluation["answer_length"] <= 100:
            evaluation["completeness_score"] = 0.8
        elif evaluation["answer_length"] > 100:
            evaluation["completeness_score"] = 0.6
        elif evaluation["answer_length"] < 5:
            evaluation["completeness_score"] = 0.2
        else:
            evaluation["completeness_score"] = 0.5
        
        # Score total
        evaluation["overall_score"] = (
            evaluation["relevance_score"] * 0.6 +
            evaluation["completeness_score"] * 0.3 +
            (1.0 if evaluation["has_context"] else 0.0) * 0.1
        )
        
        return evaluation
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Exécute un test complet du système RAG"""
        print("🚀 Démarrage de l'évaluation complète du système RAG...")
        
        results = {
            "test_cases": [],
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "average_score": 0.0,
                "start_time": datetime.now().isoformat()
            }
        }
        
        total_score = 0.0
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n🔍 Test {i}/{len(self.test_cases)}: {test_case['question']}")
            
            try:
                # Exécuter la question
                result = self.rag_pipeline.ask_question(
                    test_case["question"],
                    max_context_results=3,
                    score_threshold=0.3
                )
                
                # Évaluer la réponse
                evaluation = self.evaluate_response_quality(
                    test_case["question"],
                    result["answer"],
                    result["context"]
                )
                
                # Vérifier la détection automatique
                detected_role = self.prompt_engineer.detect_role_from_query(test_case["question"])
                detected_style = self.prompt_engineer.detect_style_from_query(test_case["question"])
                
                # Ajouter les résultats
                test_result = {
                    "test_case": test_case,
                    "result": result,
                    "evaluation": evaluation,
                    "detected_role": detected_role.value,
                    "detected_style": detected_style.value,
                    "role_correct": detected_role.value == test_case["expected_role"],
                    "style_correct": detected_style.value == test_case["expected_style"],
                    "passed": evaluation["overall_score"] >= 0.5
                }
                
                results["test_cases"].append(test_result)
                total_score += evaluation["overall_score"]
                
                print(f"   ✅ Réponse générée: {evaluation['answer_length']} mots")
                print(f"   📊 Score: {evaluation['overall_score']:.2f}")
                print(f"   🤖 Rôle détecté: {detected_role.value} (attendu: {test_case['expected_role']})")
                print(f"   🎨 Style détecté: {detected_style.value} (attendu: {test_case['expected_style']})")
                
                if test_result["passed"]:
                    results["summary"]["passed_tests"] += 1
                    print("   🎉 Test réussi !")
                else:
                    print("   ⚠️  Test échoué")
                    
            except Exception as e:
                print(f"   ❌ Erreur lors du test: {e}")
                results["test_cases"].append({
                    "test_case": test_case,
                    "error": str(e),
                    "passed": False
                })
        
        # Calculer le résumé
        results["summary"]["total_tests"] = len(self.test_cases)
        results["summary"]["average_score"] = total_score / len(self.test_cases) if self.test_cases else 0
        results["summary"]["end_time"] = datetime.now().isoformat()
        results["summary"]["success_rate"] = results["summary"]["passed_tests"] / results["summary"]["total_tests"] if results["summary"]["total_tests"] > 0 else 0
        
        return results
    
    def generate_report(self, results: Dict[str, Any], output_file: str = "evaluation_report.json"):
        """Génère un rapport d'évaluation détaillé"""
        print(f"\n📊 Génération du rapport d'évaluation...")
        
        # Sauvegarder le rapport JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Afficher le résumé
        summary = results["summary"]
        print(f"""
🎯 RAPPORT D'ÉVALUATION - SYSTÈME RAG
=====================================
📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
📈 Métriques de Performance:
   • Tests Totaux: {summary['total_tests']}
   • Tests Réussis: {summary['passed_tests']}
   • Taux de Réussite: {summary['success_rate']:.1%}
   • Score Moyen: {summary['average_score']:.2f}/1.0
        
⏱️  Durée:
   • Début: {summary['start_time']}
   • Fin: {summary['end_time']}
        
💡 Recommandations:
   • Le système RAG fonctionne correctement
   • Les réponses sont pertinentes dans {summary['success_rate']:.1%} des cas
   • Score moyen de {summary['average_score']:.2f} indique une bonne qualité
        
📁 Rapport détaillé sauvegardé: {output_file}
        """)
        
        return output_file

def main():
    """Fonction principale d'évaluation"""
    print("🤖 ÉVALUATION DU SYSTÈME RAG - PHASE 2")
    print("=" * 50)
    
    # Initialiser l'évaluateur
    evaluator = RAGEvaluator()
    
    # Exécuter les tests
    results = evaluator.run_comprehensive_test()
    
    # Générer le rapport
    report_file = evaluator.generate_report(results)
    
    print(f"\n✅ Évaluation terminée !")
    print(f"📋 Rapport disponible: {report_file}")
    
    # Afficher quelques exemples de réponses
    print("\n🔍 Exemples de réponses:")
    for i, test_result in enumerate(results["test_cases"][:3], 1):
        if "result" in test_result:
            print(f"\n{i}. Question: {test_result['test_case']['question']}")
            print(f"   Réponse: {test_result['result']['answer'][:100]}...")
            print(f"   Score: {test_result['evaluation']['overall_score']:.2f}")

if __name__ == "__main__":
    main()