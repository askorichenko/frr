module.exports = {
	rules: {
		'header-max-length': [2, 'always', 72],
		'type-case': [2, 'always', 'lower-case'],
		'type-empty': [2, 'never'],
		'type-enum': [
			2,
			'always',
			[
				'babeld',
				'bfdd',
				'bgpd',
				'build',
				'doc',
				'docker',
				'eigrpd',
				'fpm',
				'isisd',
				'ldpd',
				'lib',
				'mgmtd',
				'multi',
				'nhrpd',
				'ospf6d',
				'ospfd',
				'pathd',
				'pbrd',
				'pimd',
				'pim6d',
				'ripd',
				'ripngd',
				'sharpd',
				'staticd',
				'tests',
				'tools',
				'vtysh',
				'vrrpd',
				'yang',
				'zebra',
				'all',
			],
		],
		'subject-empty': [2, 'never'],
		'subject-full-stop': [2, 'never', '.'],
		'subject-case': [2, 'always', 'sentence-case'],
	},
};
