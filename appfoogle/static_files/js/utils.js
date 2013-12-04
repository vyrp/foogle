function getTimestamp(date){
	var dmy = date.split('/');
	if(dmy.length!=3)return NaN;
	day = dmy[0];
	month = dmy[1];
	year = dmy[2];
	mdy = [month, day, year]
	return new Date(mdy.join("/")).getTime();
}