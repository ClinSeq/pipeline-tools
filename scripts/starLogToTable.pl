#!/usr/bin/perl -w

use strict;

my @key=(); 
my @value=(); 
my $n=0; 

while(<>){
	next unless($_=~m/\|/); 
	chomp; 
	my ($k, $v) = split(/\s+\|\s+/,$_); 

	## remove leading spaces
	$v=~s/\s+//g; 

	## Convert key to CamelCase, from http://malovo.com/camel-case/converting-camelcase-perl.html
	$k=~s/\b([a-z])/\u$1/g; 

	## Remove non-alphanumerics 
	$k=~s/[^a-zA-Z0-9-]//g;
	$k=~s/\s//g;

	## remove spaces 
	$k=~s/\s//g;

	push(@key, $k); 
	push(@value, $v); 

	$n++;

}; 

## print as tab sep table
print join("\t", @key), "\n", join("\t", @value), "\n";


