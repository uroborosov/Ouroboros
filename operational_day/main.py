import pandas as pd
import os
from datetime import datetime

class OperationalDaySystem:
    def __init__(self, data_dir="data", reports_dir="reports"):
        self.data_dir = data_dir
        self.reports_dir = reports_dir
        self.ensure_directories()
        
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs(self.reports_dir, exist_ok=True)
        
    def load_data(self):
        """Load all necessary data files"""
        try:
            # Load operations list (normatives)
            operations_list_path = os.path.join(self.data_dir, "converted_operations_list.csv")
            self.operations_list = pd.read_csv(operations_list_path, delimiter=';', encoding='windows-1251')
            
            # Load operations data
            operations_path = os.path.join(self.data_dir, "converted_operations.csv")
            self.operations = pd.read_csv(operations_path, delimiter=';', encoding='windows-1251')
            
            # Load incoming flow data
            incoming_path = os.path.join(self.data_dir, "converted_incoming.csv")
            self.incoming = pd.read_csv(incoming_path, delimiter=';', encoding='windows-1251')
            
            # Load staffing data
            shr_path = os.path.join(self.data_dir, "converted_shr.csv")
            self.shr = pd.read_csv(shr_path, delimiter=';', encoding='windows-1251')
            
            print("All data files loaded successfully")
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def analyze_staff_performance(self):
        """Analyze employee performance metrics"""
        if not hasattr(self, 'operations'):
            print("Operations data not loaded")
            return None
            
        # Group by employee and calculate key metrics
        employee_stats = self.operations.groupby('ФИО').agg({
            'Кол-во операций': 'sum',
            'Выработка, %': 'mean',
            'Доля ручных операций в выработке, %': 'mean'
        }).round(2)
        
        # Reset index to make ФИО a column
        employee_stats = employee_stats.reset_index()
        
        # Sort by productivity
        employee_stats = employee_stats.sort_values('Выработка, %', ascending=False)
        
        return employee_stats
    
    def analyze_process_efficiency(self):
        """Analyze efficiency of different processes"""
        if not hasattr(self, 'operations'):
            print("Operations data not loaded")
            return None
            
        # Group by process and calculate metrics
        process_stats = self.operations.groupby('Операции').agg({
            'Кол-во операций': 'sum',
            'Выработка, %': 'mean'
        }).round(2)
        
        # Reset index to make Операции a column
        process_stats = process_stats.reset_index()
        
        # Sort by number of operations
        process_stats = process_stats.sort_values('Кол-во операций', ascending=False)
        
        return process_stats
    
    def analyze_incoming_flow(self):
        """Analyze incoming document flow by location"""
        if not hasattr(self, 'incoming'):
            print("Incoming flow data not loaded")
            return None
            
        # Sort by number of documents
        incoming_stats = self.incoming.sort_values('Кол-во принятых документов', ascending=False)
        
        return incoming_stats
    
    def analyze_staffing(self):
        """Analyze staffing structure"""
        if not hasattr(self, 'shr'):
            print("Staffing data not loaded")
            return None
            
        # Count employees by position
        position_counts = self.shr['Должность'].value_counts().reset_index()
        position_counts.columns = ['Должность', 'Количество сотрудников']
        
        # Count employees by location
        location_counts = self.shr['Населённый пункт'].value_counts().reset_index()
        location_counts.columns = ['Населённый пункт', 'Количество сотрудников']
        
        return {
            'by_position': position_counts,
            'by_location': location_counts
        }
    
    def generate_report(self, output_dir=None):
        """Generate a comprehensive markdown report"""
        if output_dir is None:
            output_dir = self.reports_dir
            
        os.makedirs(output_dir, exist_ok=True)
        
        # Create report filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(output_dir, f"operational_day_report_{timestamp}.md")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Операционный День - Отчет\n")
            f.write(f"**Дата и время генерации:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Staff Performance Analysis
            employee_stats = self.analyze_staff_performance()
            if employee_stats is not None:
                f.write(f"## Анализ производительности сотрудников\n\n")
                f.write(f"Всего сотрудников: {len(employee_stats)}\n\n")
                
                # Top performers
                top_performers = employee_stats.head(5)
                f.write(f"**Топ-5 сотрудников по выработке:**\n\n")
                for idx, row in top_performers.iterrows():
                    f.write(f"- {row['ФИО']}: {row['Выработка, %']}% (операций: {row['Кол-во операций']})\n")
                f.write(f"\n")
                
                # Bottom performers
                bottom_performers = employee_stats.tail(5)
                f.write(f"**5 сотрудников с наименьшей выработкой:**\n\n")
                for idx, row in bottom_performers.iterrows():
                    f.write(f"- {row['ФИО']}: {row['Выработка, %']}% (операций: {row['Кол-во операций']})\n")
                f.write(f"\n")
                
            # Process Efficiency Analysis
            process_stats = self.analyze_process_efficiency()
            if process_stats is not None:
                f.write(f"## Анализ эффективности процессов\n\n")
                f.write(f"Всего процессов: {len(process_stats)}\n\n")
                
                # Top processes by volume
                top_processes = process_stats.head(5)
                f.write(f"**Топ-5 процессов по объему операций:**\n\n")
                for idx, row in top_processes.iterrows():
                    f.write(f"- {row['Операции']}: {row['Кол-во операций']} операций (выработка: {row['Выработка, %']}%)\n")
                f.write(f"\n")
                
            # Incoming Flow Analysis
            incoming_stats = self.analyze_incoming_flow()
            if incoming_stats is not None:
                f.write(f"## Анализ входящего потока документов\n\n")
                f.write(f"Всего площадок: {len(incoming_stats)}\n\n")
                
                # Incoming flow by location
                f.write(f"**Поток документов по площадкам:**\n\n")
                for idx, row in incoming_stats.iterrows():
                    f.write(f"- {row['Площадка']}: {row['Кол-во принятых документов']} документов\n")
                f.write(f"\n")
                
                # Calculate totals and percentages
                total_documents = incoming_stats['Кол-во принятых документов'].sum()
                f.write(f"**Итого:** {total_documents} документов\n\n")
                
            # Staffing Analysis
            staffing_stats = self.analyze_staffing()
            if staffing_stats is not None:
                f.write(f"## Анализ структуры персонала\n\n")
                
                # Staffing by position
                f.write(f"**Сотрудники по должностям:**\n\n")
                for idx, row in staffing_stats['by_position'].iterrows():
                    f.write(f"- {row['Должность']}: {row['Количество сотрудников']}\n")
                f.write(f"\n")
                
                # Staffing by location
                f.write(f"**Сотрудники по локациям:**\n\n")
                for idx, row in staffing_stats['by_location'].iterrows():
                    f.write(f"- {row['Населённый пункт']}: {row['Количество сотрудников']}\n")
                f.write(f"\n")
            
        print(f"Report generated: {report_path}")
        return report_path
    
    def run_analysis(self):
        """Run the complete analysis pipeline"""
        print("Starting operational day analysis...")
        
        # Load data
        if not self.load_data():
            print("Failed to load data. Aborting analysis.")
            return None
        
        # Generate report
        report_path = self.generate_report()
        
        print("Analysis completed.")
        return report_path

# Example usage
if __name__ == "__main__":
    # Create system instance
    ops_system = OperationalDaySystem(data_dir="../data", reports_dir="reports")
    
    # Run analysis
    report_path = ops_system.run_analysis()
    
    if report_path:
        print(f"Analysis completed. Report saved to: {report_path}")
    else:
        print("Analysis failed.")