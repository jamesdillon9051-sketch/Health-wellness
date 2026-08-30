# -*- coding: utf-8 -*-
"""
Verified source library.

Every PubMed entry here was confirmed against the NCBI eutils API — authors,
journal, year and title all checked, not recalled. Institutional URLs were
confirmed to resolve. Nothing in this file is a study invented to fit a claim.

Add a source only after verifying it the same way:
    curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=<PMID>&retmode=json"
"""

def _pm(pmid, text):
    return '%s <a href="https://pubmed.ncbi.nlm.nih.gov/%s/">PubMed</a>.' % (text, pmid)

SOURCES = {
 # --- guidelines ---------------------------------------------------------
 'who': 'World Health Organization. <a href="https://www.who.int/publications/i/item/9789240015128">'
        '<em>WHO Guidelines on Physical Activity and Sedentary Behaviour</em></a>. 2020.',
 'nhs-guidelines': 'NHS. <a href="https://www.nhs.uk/live-well/exercise/physical-activity-guidelines-for-adults-aged-19-to-64/">'
        'Physical activity guidelines for adults aged 19 to 64</a>.',
 'nhs-strength': 'NHS. <a href="https://www.nhs.uk/live-well/exercise/strength-and-flex-exercise-plan/">'
        'Strength and Flex exercise plan</a>.',
 'nhs-exercise': 'NHS. <a href="https://www.nhs.uk/live-well/exercise/">Exercise &mdash; Live Well</a>.',
 'hhs': 'U.S. Department of Health and Human Services. <a href="https://health.gov/sites/default/files/2019-09/Physical_Activity_Guidelines_2nd_edition.pdf">'
        '<em>Physical Activity Guidelines for Americans</em>, 2nd edition</a>. 2018.',
 'medlineplus': 'MedlinePlus, U.S. National Library of Medicine. <a href="https://medlineplus.gov/exerciseandphysicalfitness.html">'
        'Exercise and Physical Fitness</a>.',
 'mayo-intensity': 'Mayo Clinic. <a href="https://www.mayoclinic.org/healthy-lifestyle/fitness/in-depth/exercise-intensity/art-20046887">'
        'Exercise intensity: How to measure it</a>.',

 # --- load, volume, frequency, effort ------------------------------------
 'schoenfeld-load': _pm('28834797',
    'Schoenfeld BJ, Grgic J, Ogborn D, Krieger JW. &ldquo;Strength and Hypertrophy Adaptations Between '
    'Low- vs. High-Load Resistance Training: A Systematic Review and Meta-analysis.&rdquo; '
    '<em>Journal of Strength and Conditioning Research</em>, 2017;31(12):3508&ndash;3523.'),
 'schoenfeld-volume': _pm('27433992',
    'Schoenfeld BJ, Ogborn D, Krieger JW. &ldquo;Dose-response relationship between weekly resistance '
    'training volume and increases in muscle mass: A systematic review and meta-analysis.&rdquo; '
    '<em>Journal of Sports Sciences</em>, 2017;35(11):1073&ndash;1082.'),
 'schoenfeld-frequency': _pm('27102172',
    'Schoenfeld BJ, Ogborn D, Krieger JW. &ldquo;Effects of Resistance Training Frequency on Measures of '
    'Muscle Hypertrophy: A Systematic Review and Meta-Analysis.&rdquo; '
    '<em>Sports Medicine</em>, 2016;46(11):1689&ndash;1697.'),
 'currier-prescription': _pm('37414459',
    'Currier BS, Mcleod JC, Banfield L, et al. &ldquo;Resistance training prescription for muscle strength '
    'and hypertrophy in healthy adults: a systematic review and Bayesian network meta-analysis.&rdquo; '
    '<em>British Journal of Sports Medicine</em>, 2023.'),
 'vieira-failure': _pm('33555822',
    'Vieira AF, Umpierre D, Teodoro JL, et al. &ldquo;Effects of Resistance Training Performed to Failure '
    'or Not to Failure on Muscle Strength, Hypertrophy, and Power Output: A Systematic Review With '
    'Meta-Analysis.&rdquo; <em>Journal of Strength and Conditioning Research</em>, 2021.'),
 'radaelli-volume': _pm('39405023',
    'Radaelli R, Rial-Vazquez J, Fernandez-Lezaun E, et al. &ldquo;Effects of Resistance Training Volume '
    'on Physical Function, Lean Body Mass and Lower-Body Muscle Hypertrophy and Strength.&rdquo; '
    '<em>Sports Medicine</em>, 2025.'),

 # --- protein and nutrition ----------------------------------------------
 'morton-protein': _pm('28698222',
    'Morton RW, Murphy KT, McKellar SR, et al. &ldquo;A systematic review, meta-analysis and '
    'meta-regression of the effect of protein supplementation on resistance training-induced gains in '
    'muscle mass and strength in healthy adults.&rdquo; '
    '<em>British Journal of Sports Medicine</em>, 2018;52(6):376&ndash;384.'),
 'nunes-protein': _pm('35187864',
    'Nunes EA, Colenso-Semple L, McKellar SR, et al. &ldquo;Systematic review and meta-analysis of protein '
    'intake to support muscle mass and function in healthy adults.&rdquo; '
    '<em>Journal of Cachexia, Sarcopenia and Muscle</em>, 2022;13(2):795&ndash;810.'),
 'pasiakos-protein': _pm('25169440',
    'Pasiakos SM, McLellan TM, Lieberman HR. &ldquo;The effects of protein supplements on muscle mass, '
    'strength, and aerobic and anaerobic power in healthy adults: a systematic review.&rdquo; '
    '<em>Sports Medicine</em>, 2015;45(1):111&ndash;131.'),

 # --- recovery, soreness, sleep ------------------------------------------
 'dupuy-recovery': _pm('29755363',
    'Dupuy O, Douzi W, Theurot D, Bosquet L, Dugu&eacute; B. &ldquo;An Evidence-Based Approach for '
    'Choosing Post-exercise Recovery Techniques to Reduce Markers of Muscle Damage, Soreness, Fatigue, '
    'and Inflammation: A Systematic Review With Meta-Analysis.&rdquo; '
    '<em>Frontiers in Physiology</em>, 2018;9:403.'),
 'herbert-stretching': _pm('21735398',
    'Herbert RD, de Noronha M, Kamper SJ. &ldquo;Stretching to prevent or reduce muscle soreness after '
    'exercise.&rdquo; <em>Cochrane Database of Systematic Reviews</em>, 2011;(7):CD004577.'),
 'cheatham-foamroll': _pm('26618062',
    'Cheatham SW, Kolber MJ, Cain M, Lee M. &ldquo;The effects of self-myofascial release using a foam '
    'roll or roller massager on joint range of motion, muscle recovery, and performance: a systematic '
    'review.&rdquo; <em>International Journal of Sports Physical Therapy</em>, 2015;10(6):827&ndash;838.'),
 'wang-heatcold': _pm('33493991',
    'Wang Y, Li S, Zhang Y, et al. &ldquo;Heat and cold therapy reduce pain in patients with delayed onset '
    'muscle soreness: A systematic review and meta-analysis of 32 randomized controlled trials.&rdquo; '
    '<em>Physical Therapy in Sport</em>, 2021;48:177&ndash;187.'),
 'bonnar-sleep': _pm('29352373',
    'Bonnar D, Bartel K, Kakoschke N, Lang C. &ldquo;Sleep Interventions Designed to Improve Athletic '
    'Performance and Recovery: A Systematic Review of Current Approaches.&rdquo; '
    '<em>Sports Medicine</em>, 2018;48(3):683&ndash;703.'),

 # --- behaviour and habit formation --------------------------------------
 'lally-habit':
    'Lally P, van Jaarsveld CHM, Potts HWW, Wardle J. &ldquo;How are habits formed: '
    'Modelling habit formation in the real world.&rdquo; <em>European Journal of Social '
    'Psychology</em>, 2010;40(6):998&ndash;1009. '
    '<a href="https://doi.org/10.1002/ejsp.674">doi:10.1002/ejsp.674</a>.',

 # --- conditioning --------------------------------------------------------
 'wu-hiit': _pm('33836261',
    'Wu ZJ, Wang ZY, Gao HE, Zhou XF, Li FH. &ldquo;Impact of high-intensity interval training on '
    'cardiorespiratory fitness, body composition, physical fitness, and metabolic parameters in older '
    'adults: A meta-analysis of randomized controlled trials.&rdquo; '
    '<em>Experimental Gerontology</em>, 2021;150:111345.'),
}


def block(keys):
    """Render a <section class="sources"> from a list of source keys.

    Returns the HTML and a slug->footnote-number map so body text can
    reference notes as <sup><a href="#source-2">2</a></sup>.
    """
    items, nums = [], {}
    for i, k in enumerate(keys, 1):
        assert k in SOURCES, 'unknown source: ' + k
        nums[k] = i
        items.append('            <li id="source-%d">%s</li>' % (i, SOURCES[k]))
    html = (u'        <section class="sources" aria-labelledby="sources-heading">\n'
            u'          <h2 id="sources-heading">Sources and further reading</h2>\n'
            u'          <ol>\n' + '\n'.join(items) + u'\n          </ol>\n'
            u'        </section>')
    return html, nums
