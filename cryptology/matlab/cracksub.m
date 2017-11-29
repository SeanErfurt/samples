function [plaintext]=cracksub(cText)
    alphabet = 'abcdefghijklmnopqrstuvwxyz';
    words = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'that', 'with', 'have', 'this', 'will'];
    sample = cText(1:75);
    [freq, relFreq] = zfrequency(cText);
	[mostFreq,indices] = sort(relFreq, 'descend');
	mfcs = char(indices+96);
    %P = perms(alphabet);
    %for i=1:size(P,1)
    for i=1:1990000
        p = randperm(26);
        p = char(p + 96);
        %swap certain ones
        p(5) = mfcs(1);
        p(mfcs(1) - 96) = 'e';
        p(20) = mfcs(2);
        p(mfcs(2) - 96) = 't';
        p(1) = mfcs(3);
        p(mfcs(3) - 96) = 'a';
        p(15) = mfcs(4);
        p(mfcs(4) - 96) = 'o';
        plaintext = substitute(p,sample);
        for w=1:length(words)
            if isempty(strfind(plaintext,w))
                %nothing
            else
                p
                plaintext
            end
        end
    end
end
    %end brute force
%     mceLetters = 'etaoinshrdl';
%     mceLetters = mceLetters - 96;
%     [freq, relFreq] = zfrequency(cText);
%     [mostFreq,indices] = sort(relFreq, 'descend');
%     mfcs = char(indices+96)
%     subKey = 'abcdefghijklmnopqrstuvwxyz';
%     subKey(5) = mfcs(1);
%     subKey(mfcs(1) - 96) = 'e';
%     subKey(20) = mfcs(2);
%     subKey(mfcs(2) - 96) = 't';
%     subKey(1) = mfcs(3);
%     subKey(mfcs(3) - 96) = 'a';
%     subKey(15) = mfcs(4);
%     subKey(mfcs(4) - 96) = 'o';
%     certain = [5 20 1 15];
%     notKey = indices(1:4);
%     % e t a o guaranteed mfcs(1:4)
%     % I N S H R D L are mixed up once
%     maxDP = 0;
%     maxIndex = -1;
%     for j=1:6
%         for i=5:11
%             eLetter = mceLetters(i);
%             sLetter = mfcs(i);
%             if any(eLetter==certain) || any((sLetter-96)==notKey)
%                 %skip replacing the certain letters
%                 % or replacing with a used letter
%             elseif any((sLetter-96)==certain)
%                 %dont swap to avoid overwriting a certain letter
%                 subKey(eLetter) = sLetter;
%             else
%                 %swap letters safely
%                 temp = subKey(eLetter);
%                 subKey(eLetter) = sLetter;
%                 subKey(sLetter - 96) = temp;
%             end
%         end
%         uniText = substitute(subKey,cText)
%         [freq, relFreq] = zfrequency(uniText);
%         dp = corr(relFreq);
%         if sum(dp) > maxDP
%             maxDP = sum(dp);
%             maxIndex = j;
%         end
%         tempL = mceLetters(j+4);
%         mceLetters(j+4) = mceLetters(j+5);
%         mceLetters(j+5) = tempL;
%     end
%     maxIndex
%     mceBigrams = {'th', 'er', 'on', 'an', 're'};
%     mfBigrams = FindMostFreq(cText, 2, 10);
%     mfBigrams = mfBigrams(:,2); %just keep the characters
%     % th er on an re are also mixed once
%     for i=1:5
%         eBG = mceBigrams{i};
%         sBG = mfBigrams{i};
%         e1 = eBG(1)-96;
%         e2 = eBG(2)-96;
%         s1 = sBG(1)-96;
%         s2 = sBG(2)-96;
%         temp1 = subKey(e1);
%         temp2 = subKey(e2);
%         if any(e1==certain) || any(s1==notKey)
%             if any(e2==certain) || any(s2==notKey)
%                 %skip replacing the certain letters
%                 % or replacing with a used letter
%             else
%                 subKey(e2) = sBG(2);
%             end
%         elseif any(e2==certain) || any(s2==notKey)
%             %skip
%         else
%             subKey(e1) = sBG(1);
%             subKey(e2) = sBG(2);
%         end
%         %swap if possible
%         if any(s1==certain)
%             if any(s2==certain)
%                 %skip replacing the certain letters
%             else
%                 subKey(s2) = temp2;
%             end
%         elseif any(s2==certain)
%             %skip
%         else
%             subKey(s1) = temp1;
%             subKey(s2) = temp2;
%         end
%     end
%     subKey
%     %2 of the, and, and tha are present
%     plaintext = substitute(subKey,cText);
% end