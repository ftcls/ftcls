(function($) {
    $.fn.jquizzy = function(settings) {
        var defaults = {
            questions: null,
            startImg: 'images/start.png',
            endText: 'Finished!',
            shortURL: null,
            sendResultsURL: null,
            resultComments: {
                comment: 'Thank you！'
            }
        };
        var config = $.extend(defaults, settings);
        if (config.questions === null) {
            $(this).html('<div class="intro-container slide-container"><h2 class="qTitle">Failed to parse questions.</h2></div>');
            return;
        }
        var superContainer = $(this),
        answers = [],
        introFob = '<div class="intro-container slide-container nav-start">Financial Texts Classification<br/><br/><a><span href="#" class="nav-start"><img src="'+config.startImg+'"></span></a></div>	',
        exitFob = '<div class="results-container slide-container"><div class="question-number">' + config.endText + '</div><div class="result-keeper"></div></div><div class="notice">Please choose Yes or No！</div><div class="progress-keeper" ><div class="progress"></div></div>',
        contentFob = '',
        questionsIteratorIndex,
        answersIteratorIndex;
        superContainer.addClass('main-quiz-holder');
        for (questionsIteratorIndex = 0; questionsIteratorIndex < config.questions.length; questionsIteratorIndex++) {
            contentFob += '<div class="slide-container"><div class="question-number">' + (questionsIteratorIndex + 1) + '/' + config.questions.length + '</div><div class="question">' + config.questions[questionsIteratorIndex].question + '</div><ul class="answers">';
            for (answersIteratorIndex = 0; answersIteratorIndex < config.questions[questionsIteratorIndex].answers.length; answersIteratorIndex++) {
                contentFob += '<li>' + config.questions[questionsIteratorIndex].answers[answersIteratorIndex] + '</li>';
            }
            contentFob += '</ul><div class="nav-container">';
            if (questionsIteratorIndex !== 0) {
                contentFob += '<div class="prev"><a class="nav-previous" href="#">&lt; Prev</a></div>';
            }
            if (questionsIteratorIndex < config.questions.length - 1) {
                contentFob += '<div class="next"><a class="nav-next" href="#">Next &gt;</a></div>';
            } else {
                contentFob += '<div class="next final"><a class="nav-show-result" href="#">Finished</a></div>';
            }
            contentFob += '</div></div>';
            answers.push(config.questions[questionsIteratorIndex].correctAnswer);
        }
        superContainer.html(introFob + contentFob + exitFob);
        var progress = superContainer.find('.progress'),
        progressKeeper = superContainer.find('.progress-keeper'),
        notice = superContainer.find('.notice'),
        progressWidth = progressKeeper.width(),
        userAnswers = [],
        questionLength = config.questions.length,
        slidesList = superContainer.find('.slide-container');
        function checkAnswers() {
            var resultArr = [],
            flag = false;
            for (i = 0; i < answers.length; i++) {
                if (answers[i] == userAnswers[i]) {
                    flag = true;
                } else {
                    flag = false;
                }
                resultArr.push(flag);
            }
            return resultArr;
        }
        function roundReloaded(num, dec) {
            var result = Math.round(num * Math.pow(10, dec)) / Math.pow(10, dec);
            return result;
        }
        
        progressKeeper.hide();
        notice.hide();
        slidesList.hide().first().fadeIn(500);
        superContainer.find('li').click(function() {
            var thisLi = $(this);
            if (thisLi.hasClass('selected')) {
                thisLi.removeClass('selected');
            } else {
                thisLi.parents('.answers').children('li').removeClass('selected');
                thisLi.addClass('selected');
            }
        });
        superContainer.find('.nav-start').click(function() {
            $(this).parents('.slide-container').fadeOut(500,
            function() {
                $(this).next().fadeIn(500);
                progressKeeper.fadeIn(500);
            });
            return false;
        });
        superContainer.find('.next').click(function() {
            if ($(this).parents('.slide-container').find('li.selected').length === 0) {
                notice.fadeIn(300);
                return false;
            }
            notice.hide();
            $(this).parents('.slide-container').fadeOut(500,
            function() {
                $(this).next().fadeIn(500);
            });
            progress.animate({
                width: progress.width() + Math.round(progressWidth / questionLength)
            },
            500);
            return false;
        });
        superContainer.find('.prev').click(function() {
            notice.hide();
            $(this).parents('.slide-container').fadeOut(500,
            function() {
                $(this).prev().fadeIn(500);
            });
            progress.animate({
                width: progress.width() - Math.round(progressWidth / questionLength)
            },
            500);
            return false;
        });
        superContainer.find('.final').click(function() {
            if ($(this).parents('.slide-container').find('li.selected').length === 0) {
                notice.fadeIn(300);
                return false;
            }
            superContainer.find('li.selected').each(function(index) {
                userAnswers.push($(this).parents('.answers').children('li').index($(this).parents('.answers').find('li.selected')) + 1);
            });
            if (config.sendResultsURL !== null) {
                var collate = [];
                for (r = 0; r < userAnswers.length; r++) {
                    collate.push('{"questionNumber":"' + parseInt(r + 1, 10) + '", "userAnswer":"' + userAnswers[r] + '"}');
                }
                
            }
            progressKeeper.hide();
            var results = checkAnswers(),
            resultSet = '',
            trueCount = 0,
            shareButton = '',
            score,
            url;
            if (config.shortURL === null) {
                config.shortURL = window.location
            };
            var resultList = [];
            for (var i = 0,toLoopTill = results.length; i < toLoopTill; i++) {
                if (results[i] === true) {
                    trueCount++;
                    isCorrect = true;
                }
                resultSet += '<div class="result-row">' + (results[i] === true ? "<div class='correct'>No: "+(i + 1)+"<span></span></div>": "<div class='result'>Text: "+(i + 1)+"<span></span></div>");
                resultSet += '<div class="resultsview-qhover">' + config.questions[i].question;
                resultSet += "<ul>";
                for (answersIteratorIndex = 0; answersIteratorIndex < config.questions[i].answers.length; answersIteratorIndex++) {
                    var classestoAdd = '';
                    
                    if (userAnswers[i] == answersIteratorIndex + 1) {
                        classestoAdd += ' selected';
                        resultList.push(userAnswers[i]);
                        if (userAnswers[i] == 1 ){
                        	resultSet += '<li class="Label_yes">label__' + userAnswers[i] + '</li>';
                        }
                        else if (userAnswers[i] == 2 ){resultSet += '<li class="Label_no">label__' + userAnswers[i] + '</li>';
                    }
                        
                    }
                    
                
                }
                resultSet += '</ul></div></div>';
            
            }
            
            
            //alert(resultList)
            var sum_Label_1 = 0;
            var sum_Label_2 = 0;
            for (var n=0; n<resultList.length;n++){
            	if (resultList[n]==1){
            		sum_Label_1++
            	}
            	else if (resultList[n]==2){
            		sum_Label_2++
            	}
            }
            resultCount = "<span style='float:left;'>Label__1(Yes): <font color='red'>"+sum_Label_1+"</font></span><span style='float:right;'>Label__2(No): <font color='green'>"+sum_Label_2+"</font></span>";
            resultSet = '<h2 class="qTitle">Your annotation results： <br/>' + resultCount + '</h2>' + shareButton + '<div class="jquizzy-clear"></div>' + resultSet + '<div class="jquizzy-clear"></div>';
            superContainer.find('.result-keeper').html(resultSet).show(500);
            
            $(this).parents('.slide-container').fadeOut(500,
            function() {
                $(this).next().fadeIn(500);
            });
            return false;
        });
    };
})(jQuery);

    var text =['初詣でに続々、「安心の年に」。「二〇〇八年が良い年になりますように」——。東京・代々木の明治神宮には一日未明、初詣での参拝客が詰めかけ、家内安全や商売繁盛などを祈願し新年を祝った。拝殿前は家族連れやカップル、カメラを構えた外国人らで身動きが取れない混雑で、カウントダウンの後、午前零時と同時に「おめでとう」の歓声と拍手。大太鼓の音が境内に響くと、賽銭が投げ入れられる音が重なった。子供のころから毎年、明治神宮で新年を迎えているという新宿区の会社役員、山口和敏さんは年男。「〇七年は食品や政治家の発言などうそが続いて不信感が募る一年だった。新年は安心できる良い年になってほしい」と願った。夫、長男と家族三人で参拝の列に並んだ足立区の女性会社員は「昨年も子供が被害にあう事件が多かった。家内安全が一番。子供が安心して暮らせる世の中になるように」 。','就寝中の父、次男が殺害、鹿児島、容疑認める。三十一日午前零時五十分ごろ、鹿児島県南さつま市笠沙町片浦、土木作業員、森美芳さんと妻、幸子さんが自宅で血まみれで倒れているのが見つかった。美芳さんは搬送先の病院で死亡、南さつま署などは同居している次男で無職の竜二容疑者を殺人と殺人未遂の疑いで逮捕した。「自分でやったと思う」と容疑を認めているという。調べによると、竜二容疑者は三十一日午前零時ごろ、自宅で寝ていた美芳さんの頭部をハンマーで数回殴り、殺害。その後、隣の居間で寝ていた幸子さんも同様に殴り、頭部陥没骨折など約一カ月のけがをさせた疑い。犯行後、竜二容疑者は「両親が血を流して倒れている」と一一九番した。自分の頭も殴り、自殺しようとしたらしい。同署は、動機や詳しい犯行の経緯について追及する。','埼玉、車36台のタイヤ、穴開けられる。埼玉県幸手市で三十日夜から三十一日朝にかけて、乗用車など計三十六台のタイヤに穴が開けられパンクしているのが見つかった。穴はキリのようなもので刺された跡とみられ、幸手署は器物損壊事件として捜査、被害に遭った車が増える可能性もあるとみて調べている。調べでは、現場は幸手市の東二、緑台二、天神島にまたがる半径約三百メートルの住宅地。車はそれぞれタイヤ一個か二個に穴を開けられ、ボンネットに引っかき傷をつけられた車もあった。付近では二十六日ごろから同様の被害が数件発生しており、幸手署は同一犯による犯行とみている。','中越地震、最後の仮設住宅閉鎖、全住民退去、新生活へ。二〇〇四年十月の新潟県中越地震で被災した旧山古志村の住民が最後まで残った「陽光台仮設住宅」が三十一日、閉鎖された。県内の仮設住宅には最大で二千九百三十五世帯、九千六百四十九人が入居したが、これで被災者全員が新しい生活の場に移った。「全住民の退去を確認し、仮設住宅を閉鎖いたします」。同日午後、青木勝山古志支所長が災害ボランティアセンターの職員らを前に仮設住宅の閉鎖となる住民の退去を宣言。陽光台仮設住宅の居住者は午前中までに退去し、センターの職員らが全戸を確認して回った。市によると、全村避難した旧山古志村の五百六十一世帯千七百七十三人が三カ所の仮設住宅に入居したのは〇四年十二月。二カ所は〇六年十二月末に閉鎖された。県は公営住宅の建設や自宅の再建が間に合わなかった世帯の居住期限を〇七年十月末に設定。大きな被害を受けた木籠集落など三十世帯については十二月三十一日まで、さらに期限を延長し、使用継続を認めていた。木籠集落の住民は二十五世帯中、十四世帯は旧山古志村に帰ったという。三十一日午前に退去した最後の居住者は、元村長の長島忠美衆院議員。「全村民が無事に退去するのを見届けたかった」と話した。','TDL遊戯施設、営業中初のぼや、100人避難、けがなし。三日午後二時半ごろ、千葉県浦安市の東京ディズニーランドでぼやがあり、アトラクション「スイスファミリー・ツリーハウス」のわらぶき屋根約十七平方メートルを焼いた。近くにいた約百人の入園客が避難、けがはなかった。運営会社のオリエンタルランドによると、一九八三年の開業以来、東京ディズニーリゾートのアトラクション施設で営業中に火災があったのは初めてという。浦安署はたばこの投げ捨ての可能性もあるとみている。','少子化一段と——新成人最少に、今年推計135万人。総務省が三十一日に発表した人口推計によると、二〇〇八年一月一日時点で二十歳の新成人は百三十五万人で、一九六八年の調査開始以来、過去最低となった。丙午年生まれが成人した八七年を初めて下回った。新成人の内訳は男性が六十九万人で、女性が六十六万人。新成人の総人口に占める割合は前年比〇・〇三ポイント低下の一・〇六%で、二年連続で過去最低を更新した。また、今年の干支にあたる「子年」生まれは千六十九万人で、男性が五百二十一万人、女性は五百四十八万人。総人口に占める割合は八・四%。出生年別では、第一次ベビーブームの四八年生まれが最多の二百二十七万人で、第二次ベビーブームの七二年生まれが百九十九万人と続いた。十二支別に人口をみると、「亥年」、「丑年」、「未年」に続いて四番目となった。','三菱化学、火災の影響拡大、汎用樹脂など出荷削減——中核設備、稼働停止続く。三菱化学は昨年十二月の鹿島事業所での火災事故を受け、汎用樹脂のポリエチレンなどの出荷量を今月から削減し始めた。事故を起こした石化基礎原料エチレンなどを生産する中核設備の稼働停止が続いているため。昨年末までの受注分は在庫や他社からの融通により確保していたが、年明けから影響が表面化し始めた。事故により、エチレンなどから生産する合成繊維原料や合成樹脂などほかの製造設備の稼働率も軒並み低下している。三菱化学は事故直後から化学各社などに原料や製品の融通を打診していたものの、事故で停止したプラント分を補う量を確保するのは難しい状況。現在は約五百社の顧客とも協議。顧客が持つ在庫や他社からの代替品調達の状況などを確認したうえで、顧客の生産活動になるべく影響を及ぼさないようにしたい考えだが、プラントの稼働再開が遅れれば一定の影響が避けられないとの見方が強い。年末には警察による事故現場周辺の封鎖が一部解除されたものの、事故の発生場所にはまだ三菱化学の社員が立ち入りできない。プラント再稼働の前提となる事故原因の本格究明にはまだ時間がかかりそうだ。','佐川子会社が二重派遣、厚労省、事業改善命令へ。日雇い派遣大手のグッドウィルが違法派遣を繰り返していた問題で、厚生労働省は七日、佐川急便グループの「佐川グローバルロジスティクス」がグッドウィルから派遣された労働者をさらに別の企業に派遣する「二重派遣」を行っていたとして、労働者派遣法に基づく事業改善命令を出す方針を固めた。物流企業が改善命令を受けるのは異例。SGLなどによると、同社は二〇〇四年十一月から昨年八月まで、グッドウィルから派遣された労働者延べ約一万一千人を大手通信販売会社の浜松市の倉庫に二重派遣し、仕分け作業などに従事させた。SGLは派遣法が定める期間を超えて労働者を働かせていたほか、派遣法で規定された適正な派遣契約をグッドウィルと結んでいなかったことも判明した。二重派遣は雇用責任があいまいになるケースが多いうえ、介在する業者の手数料などが上乗せされることで労働者の賃金が低く抑えられてしまう恐れがあるため禁じられている。厚労省は昨年十二月十九日付で処分予定をSGLに通知しており、今後同社の弁明を聞いたうえで最終的に処分内容を決める。SGLは「法令順守体制に甘さがあった。厚労省の処分は受け入れる」としている。一方、グッドウィルは二重派遣のほか派遣法で禁じられている港湾業への派遣などを繰り返していたことが発覚。厚労省は七百三十七事業所のうち違法行為があった八十九事業所に四カ月、そのほかの事業所に二カ月の事業停止命令を出す方針を固めている。','極東貿易も水増し請求、2400万円、潜水艦アンテナ納入で。防衛省は七日、海上自衛隊の潜水艦用アンテナの納入に絡み、機械商社の極東貿易が契約金額のうち約二千四百万円を過大に請求していたと発表した。同社との取引は当面停止する。同社は第三者による調査委員会で詳細を調べたうえで、過大請求分を返還する。同省によると、過大請求が行われていたのは二〇〇六年度までの五年間の五件。いずれも米国製の同型アンテナ一基を納入する契約で、金額は一件あたり二億—二億四千万円。過大請求は計二千三百七十一万円とみられるという。同省が防衛専門商社の山田洋行による過大請求を受け、過去の契約にさかのぼって調査したところ、極東貿易との契約でも同種の疑いがあることが昨年末に発覚。〇一年度分は過大請求はなかったものの見積書を偽造していたことも判明した。極東貿易は電機・エネルギー関係の機器や航空機用機材などの販売を手掛ける中堅商社で、〇六年度の防衛省との取引実績は地方分を除くと二十九件約七億四千万円。','アスキーSの会計監査人辞任。アスキーソリューションズは七日、同日付で霞が関監査法人が会計監査人を辞任したと発表した。同社は過去の決算で不適切な会計処理が発覚し、決算内容の訂正作業を進めている。同社によると、霞が関監査法人は監査対象が複数年度にまたがり、人的に対応できないことを辞任の理由に挙げたという。アスキーSは同日開いた監査役会で一時会計監査人にプライム監査法人を選任した。'];
    var content = [];

    for (var i = 0; i < text.length; i++){
        var sentence = {'question':text[i],'answers':['<font color="red">✓</font> Yes','<font color="green">✗</font> No']};
        content.push(sentence)
    };
    var init = {'questions':content};


$(function(){
    $('#quiz-container').jquizzy({
        questions: init.questions
    });
});