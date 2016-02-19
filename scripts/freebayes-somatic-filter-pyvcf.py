import vcf.filters


class FreeBayesSomaticFilter(vcf.filters.Base):
    """Keep somatic variants from freebayes"""

    name = 'freebayes-somatic'

    @classmethod
    def customize_parser(cls, parser):
        parser.add_argument('--tumor', type=str,
              help='Tumor sample name')
        parser.add_argument('--normal', type=str,
              help='Normal sample name')
        parser.add_argument('--n_lod_threshold', type=float, default=3.5,
              help='Normal LOD threshold')
        parser.add_argument('--t_lod_threshold', type=float, default=3.5,
              help='Tumor LOD threshold')

    def __init__(self, args):
        self.threshold = {"t_lod_threshold":args.t_lod_threshold,
                          "n_lod_threshold":args.t_lod_threshold}
        self.tumorid = args.tumor
        self.normalid = args.normal

    def __call__(self, record):
        tumor_gt = [r for r in record.samples if r.sample == self.tumorid][0]
        normal_gt = [r for r in record.samples if r.sample == self.normalid][0]
        tumor_lod = max(tumor_gt.data.GL[i] - tumor_gt.data.GL[0] for i in range(1, len(tumor_gt.data.GL)))
        normal_lod = min(normal_gt.data.GL[0] - normal_gt.data.GL[i] for i in range(1, len(normal_gt.data.GL)))
        is_somatic = normal_lod >= self.threshold["n_lod_threshold"] and tumor_lod >= self.threshold["t_lod_threshold"]
        if not is_somatic:
            return 1

    def filter_name(self):
        return "REJECT_GERMLINE"