package main

import (
	"os"
	"fmt"
	"bufio"
	"strings"
	"strconv"

	sort2 "sort"
)

type IR struct {
	Name string
	Num float64
}

type IRs []IR

func ReadFile (filePath string) (IRs , error) {

	file, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	var ir IR
	var irs IRs
	i := 0
	for scanner.Scan() {
		line := scanner.Text()
		tmp := strings.Split(line, " ")
		num, err := strconv.ParseFloat(tmp[1], 10)
		if err != nil {
			return nil, err
		}

		ir.Name = tmp[0]
		ir.Num = num
		irs = append(irs, ir)
		i++
		//fmt.Println(string(line))
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}
	return irs, nil
}


func (v IRs) Len() int {
	return len(v)
}

func (v IRs) Swap(i, j int) {
	v[i], v[j] = v[j], v[i]
}

func (v IRs) Less(i, j int) bool {
	return v[i].Num < v[j].Num
}



func sort(irs IRs) {

	sort2.Sort(irs)

}

func main()  {
	result, err := ReadFile(`C:\GOPATH\src\IRProject\src\result.txt`)
	if err != nil {
		fmt.Println(err)
	}

	sort(result)
	for _, v := range result{
		fmt.Println(v)
		}
}
