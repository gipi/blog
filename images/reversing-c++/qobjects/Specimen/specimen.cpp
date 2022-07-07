#include "specimen.h"
#include "./ui_specimen.h"

Specimen::Specimen(QWidget *parent)
    : QMainWindow(parent) , ui(new Ui::Specimen), kebab(parent)
{
    ui->setupUi(this);
}

Specimen::~Specimen()
{
    delete ui;
}

void Specimen::changeSauce(Kebab::Sauce sauce) {
    this->kebab.setSauce(sauce);
}
