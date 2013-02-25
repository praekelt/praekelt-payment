def get_network_operator(msisdn):
    mapping = (
        ('2783', 'MTN'),
        ('2773', 'MTN'),
        ('2778', 'MTN'),
        ('27710', 'MTN'),
        ('27717', 'MTN'),
        ('27718', 'MTN'),
        ('27719', 'MTN'),
        ('2782', 'VOD'),
        ('2772', 'VOD'),
        ('2776', 'VOD'),
        ('2779', 'VOD'),
        ('27711', 'VOD'),
        ('27712', 'VOD'),
        ('27713', 'VOD'),
        ('27714', 'VOD'),
        ('27715', 'VOD'),
        ('27716', 'VOD'),
        ('2784', 'CELLC'),
        ('2774', 'CELLC'),
        ('27811', '8TA'),
        ('27812', '8TA'),
        ('27813', '8TA'),
        ('27814', '8TA'),
        )

    for prefix, op in mapping:
        if msisdn.startswith(prefix):
            return op
    return None
