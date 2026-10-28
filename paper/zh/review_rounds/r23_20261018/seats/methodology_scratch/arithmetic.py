"""Read only manuscript arithmetic checks; no EDA, source import, or peer inputs."""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal, ROUND_HALF_UP
import hashlib, json, re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'inputs/manuscript_numbered.txt'
text = SOURCE.read_text(encoding='utf-8')

def table(label):
    return text.split('\\label{' + label + '}', 1)[1].split('\\end{table}', 1)[0]

def rows(label):
    result = []
    for line in table(label).splitlines():
        line = re.sub(r'^\d+: ', '', line)
        if re.match(r'^s\d+\s*&', line):
            cells = line.split('&')
            nums = []
            for c in cells[1:]:
                m = re.search(r'[-+]?\d+(?:\.\d+)?', c)
                nums.append(m.group(0) if m else None)
            result.append((cells[0].strip(), nums))
    return result

result = {'scope': 'Manuscript-internal arithmetic only; no replication of reported experiments.',
          'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest()}
ablation = rows('tab:ablation')
result['ablation_means_from_printed_rows'] = []
for j, name in enumerate(['G', 'B', 'random', 'mixed']):
    values = [Fraction(x[1][j]) for x in ablation]
    exact = sum(values) / len(values)
    result['ablation_means_from_printed_rows'].append({'column': name, 'values': [str(v) for v in values], 'sum': str(sum(values)), 'n': len(values), 'mean_exact': str(exact), 'mean_decimal': float(exact), 'nearest_0.01_if_half_up': str((Decimal(exact.numerator)/Decimal(exact.denominator)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))})
eff = rows('tab:efficiency')
result['first_improvement_STA'] = []
for name, nums in eff:
    seeds = [int(v) for v in nums[1:4]]
    mean = Fraction(sum(seeds), 3)
    result['first_improvement_STA'].append({'circuit': name, 'mixed': nums[0], 'seeds': seeds, 'reported_mean': nums[4], 'mean_exact': str(mean), 'mean_decimal': float(mean), 'seed_ratio': str(Fraction(max(seeds), min(seeds))), 'mixed_less_than_seed_mean': None if nums[0] is None else Fraction(nums[0]) < mean})
result['mixed_less_count'] = sum(x['mixed_less_than_seed_mean'] is True for x in result['first_improvement_STA'])
result['available_mixed_count'] = sum(x['mixed_less_than_seed_mean'] is not None for x in result['first_improvement_STA'])
result['runtime_random_STA_mean'] = {'values': [2439,2476,2527], 'sum': 7442, 'n': 3, 'mean_exact': str(Fraction(7442,3)), 'mean_decimal': float(Fraction(7442,3)), 'reported': '2480.7', 'rounding_rule_in_manuscript': 'unstated'}
result['F4_fraction'] = {'numerator':2434,'denominator':4044,'exact':str(Fraction(2434,4044)), 'percent':float(Fraction(243400,4044)), 'reported_percent':'60.2'}
result['F1_F6_sum'] = sum([138,3,16,2434,915,0])
result['candidate_record_batch_reconciliation'] = {'old_total':4044,'old_b17':785,'new_b17':104,'replaced_total':4044-785+104,'reported_new_total':3363}
pr = rows('tab:pr8')
result['physical_deltas'] = [{'circuit': name, 'calculated_delta':str(Fraction(nums[3])-Fraction(nums[2])), 'reported_delta':nums[4]} for name,nums in pr]
result['physical_sign_counts'] = {k:sum((Fraction(x['calculated_delta'])>0 if k=='positive' else Fraction(x['calculated_delta'])<0 if k=='negative' else Fraction(x['calculated_delta'])==0) for x in result['physical_deltas']) for k in ['positive','zero','negative']}
result['S_WNS_partition'] = {'positive':0,'zero':36,'negative':90,'sum':0+36+90,'reported_total':126}
access = []
for relative in ['contract.json','metadata.json','seats/methodology_phase1.md','seats/methodology_phase2_input.txt','inputs/manuscript_numbered.txt','inputs/manuscript_pdf_text.txt']:
    p = ROOT / relative
    b = p.read_bytes()
    access.append({'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
result['read_file_receipt'] = access
print(json.dumps(result, ensure_ascii=False, indent=2))
