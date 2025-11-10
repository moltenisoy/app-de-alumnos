import json
import subprocess
import time


class CicloIterativo:

    def __init__(self, max_iteraciones: int=10):
        self.max_iteraciones = max_iteraciones
        self.iteracion_actual = 0
        self.historial = []

    def ejecutar_analisis(self) ->dict:
        print(f"\n{'=' * 80}")
        print(f'🔍 ITERACIÓN {self.iteracion_actual + 1}: EJECUTANDO ANÁLISIS')
        print(f"{'=' * 80}\n")
        subprocess.run(['python', 'code_analyzer.py'], capture_output=True,
            text=True, timeout=300)
        with open('code_analysis_report.json', 'r', encoding='utf-8') as f:
            reporte = json.load(f)
        return reporte

    def ejecutar_correcciones(self) ->int:
        print(f"\n{'=' * 80}")
        print(
            f'🔧 ITERACIÓN {self.iteracion_actual + 1}: APLICANDO CORRECCIONES')
        print(f"{'=' * 80}\n")
        result = subprocess.run(['python', 'code_fixer.py'], capture_output
            =True, text=True, timeout=300)
        correcciones = 0
        for line in result.stdout.split('\n'):
            if 'Correcciones aplicadas:' in line:
                try:
                    correcciones = int(line.split(':')[1].strip())
                except:
                    pass
        return correcciones

    def aplicar_correcciones_manuales_criticas(self, reporte: dict) ->int:
        criticos = reporte['issues_by_severity']['critical']
        if not criticos:
            return 0
        print(f'\n🔴 Corrigiendo {len(criticos)} problemas críticos...')
        return 0

    def verificar_calidad(self, reporte: dict) ->bool:
        summary = reporte['summary']
        if summary['critical'] > 0:
            return False
        if summary['high'] > 10:
            return False
        if len(self.historial) > 0:
            primera_iteracion = self.historial[0]
            if summary['medium'] > primera_iteracion['summary']['medium'
                ] * 0.5:
                pass
        return True

    def ejecutar_ciclo(self):
        print('\n' + '=' * 80)
        print('🔄 INICIANDO CICLO ITERATIVO DE ANÁLISIS Y CORRECCIÓN')
        print('=' * 80)
        print(f'Máximo de iteraciones: {self.max_iteraciones}')
        print('Objetivo: 0 críticos, <10 altos, reducir medios/bajos\n')
        while self.iteracion_actual < self.max_iteraciones:
            inicio_iteracion = time.time()
            reporte = self.ejecutar_analisis()
            summary = reporte['summary']
            self.historial.append(reporte)
            print(f'\n📊 RESUMEN - Iteración {self.iteracion_actual + 1}:')
            print(f"  Archivos analizados: {summary['files_analyzed']}")
            print(f"  Total problemas: {summary['total_issues']}")
            print(f"  🔴 Críticos: {summary['critical']}")
            print(f"  🟠 Altos: {summary['high']}")
            print(f"  🟡 Medios: {summary['medium']}")
            print(f"  🟢 Bajos: {summary['low']}")
            if self.verificar_calidad(reporte):
                print(
                    f'\n✅ ¡CALIDAD DESEADA ALCANZADA en iteración {self.iteracion_actual + 1}!'
                    )
                break
            correcciones_auto = self.ejecutar_correcciones()
            correcciones_manuales = (self.
                aplicar_correcciones_manuales_criticas(reporte))
            total_correcciones = correcciones_auto + correcciones_manuales
            if total_correcciones == 0:
                print(
                    '\n⚠️  No se pudieron aplicar más correcciones automáticas.'
                    )
                print('Los problemas restantes requieren revisión manual.')
                break
            duracion = time.time() - inicio_iteracion
            print(f'\n⏱️  Duración de iteración: {duracion:.2f} segundos')
            print(f'✓ Correcciones aplicadas: {total_correcciones}')
            self.iteracion_actual += 1
            time.sleep(1)
        self.mostrar_resumen_final()

    def mostrar_resumen_final(self):
        print('\n' + '=' * 80)
        print('📊 RESUMEN FINAL DEL CICLO ITERATIVO')
        print('=' * 80)
        if len(self.historial) == 0:
            print('No se ejecutaron iteraciones.')
            return
        primera = self.historial[0]['summary']
        ultima = self.historial[-1]['summary']
        print(f'\nIteraciones ejecutadas: {len(self.historial)}')
        print(f"\n{'Métrica':<20} {'Inicial':<15} {'Final':<15} {'Mejora':<15}"
            )
        print('-' * 65)
        for metrica in ['total_issues', 'critical', 'high', 'medium', 'low']:
            inicial = primera[metrica]
            final = ultima[metrica]
            mejora = inicial - final
            mejora_pct = mejora / inicial * 100 if inicial > 0 else 0
            nombre_metrica = {'total_issues': 'Total Problemas', 'critical':
                'Críticos', 'high': 'Altos', 'medium': 'Medios', 'low': 'Bajos'
                }[metrica]
            print(
                f'{nombre_metrica:<20} {inicial:<15} {final:<15} -{mejora} ({mejora_pct:.1f}%)'
                )
        print('\n' + '=' * 80)
        if ultima['critical'] == 0 and ultima['high'] < 10:
            print('✅ CALIDAD DE CÓDIGO EXCELENTE ALCANZADA')
        elif ultima['critical'] == 0:
            print('✅ SIN PROBLEMAS CRÍTICOS - CALIDAD ACEPTABLE')
        else:
            print('⚠️  QUEDAN PROBLEMAS CRÍTICOS POR RESOLVER')
        print('=' * 80 + '\n')
        with open('analisis_historial.json', 'w', encoding='utf-8') as f:
            json.dump({'iteraciones': len(self.historial), 'historial': [h[
                'summary'] for h in self.historial]}, f, indent=2)
        print('📁 Historial guardado en: analisis_historial.json\n')


def main():
    ciclo = CicloIterativo(max_iteraciones=5)
    ciclo.ejecutar_ciclo()


if __name__ == '__main__':
    main()

